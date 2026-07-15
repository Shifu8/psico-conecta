BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS pagos_schema;

-- Conservar las tablas demostrativas antiguas si todavía usan IDs seriales
-- o no contienen la relación obligatoria con una cita.
DO $$
DECLARE
    tipo_id TEXT;
    estructura_completa BOOLEAN;
BEGIN
    IF to_regclass('pagos_schema.pagos') IS NOT NULL THEN
        SELECT data_type INTO tipo_id
        FROM information_schema.columns
        WHERE table_schema = 'pagos_schema' AND table_name = 'pagos' AND column_name = 'id';

        SELECT COUNT(*) = 12 INTO estructura_completa
        FROM information_schema.columns
        WHERE table_schema = 'pagos_schema'
          AND table_name = 'pagos'
          AND column_name IN (
              'cita_id','paciente_id','psicologo_id','monto_centavos','estado',
              'fecha_hora_inicio','fecha_hora_fin','stripe_checkout_session_id',
              'stripe_payment_intent_id','reembolsado_centavos','creado_en','actualizado_en'
          );

        IF tipo_id IS DISTINCT FROM 'uuid' OR NOT estructura_completa THEN
            IF to_regclass('pagos_schema.pagos_legacy_v1') IS NULL THEN
                ALTER TABLE pagos_schema.pagos RENAME TO pagos_legacy_v1;
            ELSE
                ALTER TABLE pagos_schema.pagos RENAME TO pagos_legacy_v1_extra;
            END IF;
        END IF;
    END IF;
END $$;

DO $$
DECLARE
    tipo_id TEXT;
    tiene_evento BOOLEAN;
BEGIN
    IF to_regclass('pagos_schema.transacciones') IS NOT NULL THEN
        SELECT data_type INTO tipo_id
        FROM information_schema.columns
        WHERE table_schema = 'pagos_schema' AND table_name = 'transacciones' AND column_name = 'id';

        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'pagos_schema' AND table_name = 'transacciones' AND column_name = 'proveedor_evento_id'
        ) INTO tiene_evento;

        IF tipo_id IS DISTINCT FROM 'uuid' OR NOT tiene_evento THEN
            IF to_regclass('pagos_schema.transacciones_legacy_v1') IS NULL THEN
                ALTER TABLE pagos_schema.transacciones RENAME TO transacciones_legacy_v1;
            ELSE
                ALTER TABLE pagos_schema.transacciones RENAME TO transacciones_legacy_v1_extra;
            END IF;
        END IF;
    END IF;
END $$;

DO $$
BEGIN
    IF to_regclass('pagos_schema.comprobantes') IS NOT NULL
       AND to_regclass('pagos_schema.comprobantes_legacy_v1') IS NULL THEN
        ALTER TABLE pagos_schema.comprobantes RENAME TO comprobantes_legacy_v1;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS pagos_schema.pagos (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    cita_id UUID NOT NULL,
    paciente_id INTEGER NOT NULL,
    psicologo_id INTEGER NOT NULL,
    monto_centavos INTEGER NOT NULL,
    moneda VARCHAR(3) NOT NULL DEFAULT 'USD',
    estado VARCHAR(32) NOT NULL DEFAULT 'PENDIENTE',
    proveedor VARCHAR(20) NOT NULL DEFAULT 'STRIPE',
    modalidad VARCHAR(15) NOT NULL DEFAULT 'VIRTUAL',
    fecha_hora_inicio TIMESTAMPTZ NOT NULL,
    fecha_hora_fin TIMESTAMPTZ NOT NULL,
    stripe_checkout_session_id VARCHAR(255),
    stripe_payment_intent_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    checkout_url TEXT,
    checkout_expira_en TIMESTAMPTZ,
    comprobante_url TEXT,
    reembolsado_centavos INTEGER NOT NULL DEFAULT 0,
    ultimo_error TEXT,
    pagado_en TIMESTAMPTZ,
    cancelado_en TIMESTAMPTZ,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT pagos_pkey_v2 PRIMARY KEY (id),
    CONSTRAINT uq_pagos_cita UNIQUE (cita_id),
    CONSTRAINT uq_pagos_checkout UNIQUE (stripe_checkout_session_id),
    CONSTRAINT uq_pagos_payment_intent UNIQUE (stripe_payment_intent_id),
    CONSTRAINT ck_pagos_estado CHECK (
        estado IN (
            'PENDIENTE','CHECKOUT_ABIERTO','PROCESANDO','PAGADO','FALLIDO',
            'EXPIRADO','CANCELADO','REEMBOLSO_PENDIENTE','REEMBOLSO_PARCIAL',
            'REEMBOLSADO','REPROGRAMACION_PENDIENTE','DISPUTADO'
        )
    ),
    CONSTRAINT ck_pagos_monto_positivo CHECK (monto_centavos > 0),
    CONSTRAINT ck_pagos_reembolso_no_negativo CHECK (reembolsado_centavos >= 0),
    CONSTRAINT ck_pagos_reembolso_limite CHECK (reembolsado_centavos <= monto_centavos),
    CONSTRAINT ck_pagos_rango_fecha CHECK (fecha_hora_fin > fecha_hora_inicio)
);

CREATE INDEX IF NOT EXISTS ix_pagos_cita ON pagos_schema.pagos (cita_id);
CREATE INDEX IF NOT EXISTS ix_pagos_paciente_creado ON pagos_schema.pagos (paciente_id, creado_en DESC);
CREATE INDEX IF NOT EXISTS ix_pagos_psicologo_creado ON pagos_schema.pagos (psicologo_id, creado_en DESC);
CREATE INDEX IF NOT EXISTS ix_pagos_estado ON pagos_schema.pagos (estado);

CREATE TABLE IF NOT EXISTS pagos_schema.transacciones (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    pago_id UUID NOT NULL,
    tipo VARCHAR(80) NOT NULL,
    estado VARCHAR(40) NOT NULL,
    monto_centavos INTEGER,
    proveedor_evento_id VARCHAR(255),
    datos JSONB,
    registrado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT transacciones_pkey_v2 PRIMARY KEY (id),
    CONSTRAINT fk_transacciones_pago FOREIGN KEY (pago_id)
        REFERENCES pagos_schema.pagos(id) ON DELETE CASCADE,
    CONSTRAINT uq_transacciones_evento UNIQUE (proveedor_evento_id)
);

CREATE INDEX IF NOT EXISTS ix_transacciones_pago_fecha
    ON pagos_schema.transacciones (pago_id, registrado_en);

CREATE TABLE IF NOT EXISTS pagos_schema.reembolsos (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    pago_id UUID NOT NULL,
    solicitado_por INTEGER,
    monto_centavos INTEGER NOT NULL,
    razon VARCHAR(40) NOT NULL DEFAULT 'requested_by_customer',
    nota TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    stripe_refund_id VARCHAR(255),
    ultimo_error TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT reembolsos_pkey_v2 PRIMARY KEY (id),
    CONSTRAINT fk_reembolsos_pago FOREIGN KEY (pago_id)
        REFERENCES pagos_schema.pagos(id) ON DELETE CASCADE,
    CONSTRAINT uq_reembolsos_stripe UNIQUE (stripe_refund_id),
    CONSTRAINT ck_reembolsos_estado CHECK (
        estado IN ('PENDIENTE','PROCESANDO','EXITOSO','FALLIDO','CANCELADO')
    ),
    CONSTRAINT ck_reembolsos_monto_positivo CHECK (monto_centavos > 0)
);

CREATE INDEX IF NOT EXISTS ix_reembolsos_pago_fecha
    ON pagos_schema.reembolsos (pago_id, creado_en);

CREATE TABLE IF NOT EXISTS pagos_schema.tarifas (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    psicologo_id INTEGER,
    modalidad VARCHAR(15) NOT NULL DEFAULT 'TODAS',
    monto_centavos INTEGER NOT NULL,
    moneda VARCHAR(3) NOT NULL DEFAULT 'USD',
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    creado_por INTEGER,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT tarifas_pkey_v2 PRIMARY KEY (id),
    CONSTRAINT ck_tarifas_modalidad CHECK (modalidad IN ('TODAS','VIRTUAL','PRESENCIAL')),
    CONSTRAINT ck_tarifas_monto_positivo CHECK (monto_centavos > 0)
);

CREATE INDEX IF NOT EXISTS ix_tarifas_busqueda
    ON pagos_schema.tarifas (psicologo_id, modalidad, activa, creado_en DESC);

COMMIT;
