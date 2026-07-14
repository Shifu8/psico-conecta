BEGIN;

CREATE SCHEMA IF NOT EXISTS citas_schema;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- La versión antigua tenía id SERIAL y una columna "fecha". Se conserva como respaldo.
DO $$
DECLARE
    tipo_id TEXT;
BEGIN
    IF to_regclass('citas_schema.citas') IS NOT NULL THEN
        SELECT data_type INTO tipo_id
        FROM information_schema.columns
        WHERE table_schema = 'citas_schema'
          AND table_name = 'citas'
          AND column_name = 'id';

        IF tipo_id IS DISTINCT FROM 'uuid' THEN
            IF to_regclass('citas_schema.citas_legacy_v1') IS NOT NULL THEN
                RAISE EXCEPTION 'Ya existe citas_schema.citas_legacy_v1. Revísala antes de repetir la migración.';
            END IF;
            ALTER TABLE citas_schema.citas RENAME TO citas_legacy_v1;
        END IF;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS citas_schema.disponibilidad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    psicologo_id INTEGER NOT NULL,
    dia_semana SMALLINT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    duracion_slot SMALLINT NOT NULL DEFAULT 50,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS citas_schema.excepciones_disponibilidad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    psicologo_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    motivo VARCHAR(255),
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS citas_schema.citas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id INTEGER NOT NULL,
    psicologo_id INTEGER NOT NULL,
    fecha_hora_inicio TIMESTAMPTZ NOT NULL,
    fecha_hora_fin TIMESTAMPTZ NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    modalidad VARCHAR(15) NOT NULL DEFAULT 'VIRTUAL',
    motivo_consulta TEXT,
    notas_psicologo TEXT,
    motivo_cancelacion TEXT,
    cancelado_por INTEGER,
    reprogramada_desde UUID,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS citas_schema.historial_cambios_citas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cita_id UUID NOT NULL,
    accion VARCHAR(40) NOT NULL DEFAULT 'CAMBIO_ESTADO',
    estado_anterior VARCHAR(20),
    estado_nuevo VARCHAR(20) NOT NULL,
    cambiado_por INTEGER NOT NULL,
    motivo TEXT,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    fecha_cambio TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE citas_schema.historial_cambios_citas
    ADD COLUMN IF NOT EXISTS accion VARCHAR(40) NOT NULL DEFAULT 'CAMBIO_ESTADO',
    ADD COLUMN IF NOT EXISTS datos_anteriores JSONB,
    ADD COLUMN IF NOT EXISTS datos_nuevos JSONB;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_disponibilidad_dia') THEN
        ALTER TABLE citas_schema.disponibilidad
            ADD CONSTRAINT ck_disponibilidad_dia CHECK (dia_semana BETWEEN 0 AND 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_disponibilidad_horas') THEN
        ALTER TABLE citas_schema.disponibilidad
            ADD CONSTRAINT ck_disponibilidad_horas CHECK (hora_fin > hora_inicio);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_disponibilidad_duracion') THEN
        ALTER TABLE citas_schema.disponibilidad
            ADD CONSTRAINT ck_disponibilidad_duracion CHECK (duracion_slot BETWEEN 15 AND 180);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_disponibilidad_bloque') THEN
        ALTER TABLE citas_schema.disponibilidad
            ADD CONSTRAINT uq_disponibilidad_bloque UNIQUE (psicologo_id, dia_semana, hora_inicio, hora_fin);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_excepcion_psicologo_fecha') THEN
        ALTER TABLE citas_schema.excepciones_disponibilidad
            ADD CONSTRAINT uq_excepcion_psicologo_fecha UNIQUE (psicologo_id, fecha);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_citas_estado') THEN
        ALTER TABLE citas_schema.citas
            ADD CONSTRAINT ck_citas_estado CHECK (estado IN ('PENDIENTE','CONFIRMADA','REPROGRAMADA','CANCELADA','COMPLETADA','NO_ASISTIDA'));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_citas_modalidad') THEN
        ALTER TABLE citas_schema.citas
            ADD CONSTRAINT ck_citas_modalidad CHECK (modalidad IN ('VIRTUAL','PRESENCIAL'));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_citas_rango_fecha') THEN
        ALTER TABLE citas_schema.citas
            ADD CONSTRAINT ck_citas_rango_fecha CHECK (fecha_hora_fin > fecha_hora_inicio);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_disponibilidad_psicologo_dia
    ON citas_schema.disponibilidad (psicologo_id, dia_semana);
CREATE INDEX IF NOT EXISTS ix_excepcion_psicologo_fecha
    ON citas_schema.excepciones_disponibilidad (psicologo_id, fecha);
CREATE INDEX IF NOT EXISTS ix_citas_psicologo_inicio
    ON citas_schema.citas (psicologo_id, fecha_hora_inicio);
CREATE INDEX IF NOT EXISTS ix_citas_paciente_inicio
    ON citas_schema.citas (paciente_id, fecha_hora_inicio);
CREATE INDEX IF NOT EXISTS ix_citas_estado
    ON citas_schema.citas (estado);
CREATE INDEX IF NOT EXISTS ix_historial_cita_fecha
    ON citas_schema.historial_cambios_citas (cita_id, fecha_cambio);

COMMIT;
