BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS teleconsulta_schema;

DO $$
DECLARE
    tipo_cita TEXT;
    tipo_id TEXT;
BEGIN
    IF to_regclass('teleconsulta_schema.sesiones_zoom') IS NOT NULL THEN
        SELECT data_type INTO tipo_cita
        FROM information_schema.columns
        WHERE table_schema = 'teleconsulta_schema'
          AND table_name = 'sesiones_zoom'
          AND column_name = 'cita_id';

        SELECT data_type INTO tipo_id
        FROM information_schema.columns
        WHERE table_schema = 'teleconsulta_schema'
          AND table_name = 'sesiones_zoom'
          AND column_name = 'id';

        IF tipo_cita IS DISTINCT FROM 'uuid' OR tipo_id IS DISTINCT FROM 'uuid' THEN
            IF to_regclass('teleconsulta_schema.sesiones_zoom_legacy_v1') IS NULL THEN
                ALTER TABLE teleconsulta_schema.sesiones_zoom RENAME TO sesiones_zoom_legacy_v1;
            ELSE
                DROP TABLE teleconsulta_schema.sesiones_zoom;
            END IF;
        END IF;
    END IF;

    IF to_regclass('teleconsulta_schema.historial_sesiones') IS NOT NULL THEN
        SELECT data_type INTO tipo_id
        FROM information_schema.columns
        WHERE table_schema = 'teleconsulta_schema'
          AND table_name = 'historial_sesiones'
          AND column_name = 'id';

        IF tipo_id IS DISTINCT FROM 'uuid' THEN
            IF to_regclass('teleconsulta_schema.historial_sesiones_legacy_v1') IS NULL THEN
                ALTER TABLE teleconsulta_schema.historial_sesiones RENAME TO historial_sesiones_legacy_v1;
            ELSE
                DROP TABLE teleconsulta_schema.historial_sesiones;
            END IF;
        END IF;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS teleconsulta_schema.sesiones_zoom (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cita_id UUID NOT NULL UNIQUE,
    paciente_id INTEGER NOT NULL,
    psicologo_id INTEGER NOT NULL,
    zoom_meeting_id VARCHAR(32) UNIQUE,
    zoom_meeting_uuid VARCHAR(255),
    zoom_host_user_id VARCHAR(255),
    tema VARCHAR(255) NOT NULL DEFAULT 'Teleconsulta PsicoConecta',
    enlace_acceso TEXT,
    contrasena VARCHAR(64),
    fecha_hora_inicio TIMESTAMPTZ NOT NULL,
    fecha_hora_fin TIMESTAMPTZ NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PROGRAMADA',
    ultimo_error TEXT,
    ultima_sincronizacion_zoom TIMESTAMPTZ,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_sesiones_zoom_estado CHECK (
        estado IN ('PROGRAMADA','EN_CURSO','FINALIZADA','CANCELADA','ERROR')
    ),
    CONSTRAINT ck_sesiones_zoom_rango CHECK (fecha_hora_fin > fecha_hora_inicio)
);

CREATE INDEX IF NOT EXISTS ix_sesiones_zoom_cita
    ON teleconsulta_schema.sesiones_zoom (cita_id);
CREATE INDEX IF NOT EXISTS ix_sesiones_zoom_psicologo_inicio
    ON teleconsulta_schema.sesiones_zoom (psicologo_id, fecha_hora_inicio);
CREATE INDEX IF NOT EXISTS ix_sesiones_zoom_paciente_inicio
    ON teleconsulta_schema.sesiones_zoom (paciente_id, fecha_hora_inicio);
CREATE INDEX IF NOT EXISTS ix_sesiones_zoom_estado
    ON teleconsulta_schema.sesiones_zoom (estado);

CREATE TABLE IF NOT EXISTS teleconsulta_schema.historial_sesiones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sesion_id UUID NOT NULL,
    evento VARCHAR(80) NOT NULL,
    actor_id INTEGER,
    data JSONB,
    registrado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_historial_sesion FOREIGN KEY (sesion_id)
        REFERENCES teleconsulta_schema.sesiones_zoom(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_historial_sesion_fecha
    ON teleconsulta_schema.historial_sesiones (sesion_id, registrado_en);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_historial_sesion'
          AND conrelid = 'teleconsulta_schema.historial_sesiones'::regclass
    ) THEN
        ALTER TABLE teleconsulta_schema.historial_sesiones
            ADD CONSTRAINT fk_historial_sesion
            FOREIGN KEY (sesion_id)
            REFERENCES teleconsulta_schema.sesiones_zoom(id)
            ON DELETE CASCADE;
    END IF;
END $$;

COMMIT;
