CREATE SCHEMA IF NOT EXISTS usuarios_schema;
CREATE SCHEMA IF NOT EXISTS citas_schema;
CREATE SCHEMA IF NOT EXISTS teleconsulta_schema;
CREATE SCHEMA IF NOT EXISTS pagos_schema;

-- Servicio de usuarios
CREATE TABLE IF NOT EXISTS usuarios_schema.roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(40) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS usuarios_schema.permisos (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS usuarios_schema.roles_permisos (
    rol_id INTEGER NOT NULL,
    permiso_id INTEGER NOT NULL,
    PRIMARY KEY (rol_id, permiso_id),
    FOREIGN KEY (rol_id) REFERENCES usuarios_schema.roles(id),
    FOREIGN KEY (permiso_id) REFERENCES usuarios_schema.permisos(id)
);

CREATE TABLE IF NOT EXISTS usuarios_schema.usuarios (
    id SERIAL PRIMARY KEY,
    cognito_sub VARCHAR(255) UNIQUE,
    google_id VARCHAR(255) UNIQUE,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    birth_date DATE,
    role_id INTEGER NOT NULL REFERENCES usuarios_schema.roles(id),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS usuarios_schema.tokens_recuperacion (
    id SERIAL PRIMARY KEY,
    token_hash VARCHAR(64) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES usuarios_schema.usuarios(id),
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuarios_schema.tokens_revocados (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(64) UNIQUE NOT NULL,
    revoked_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Servicio de citas
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS citas_schema.disponibilidad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    psicologo_id INTEGER NOT NULL,
    dia_semana SMALLINT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    duracion_slot SMALLINT NOT NULL DEFAULT 50,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_disponibilidad_dia CHECK (dia_semana BETWEEN 0 AND 6),
    CONSTRAINT ck_disponibilidad_horas CHECK (hora_fin > hora_inicio),
    CONSTRAINT ck_disponibilidad_duracion CHECK (duracion_slot BETWEEN 15 AND 180),
    CONSTRAINT uq_disponibilidad_bloque UNIQUE (psicologo_id, dia_semana, hora_inicio, hora_fin)
);

CREATE INDEX IF NOT EXISTS ix_disponibilidad_psicologo_dia
    ON citas_schema.disponibilidad (psicologo_id, dia_semana);

CREATE TABLE IF NOT EXISTS citas_schema.excepciones_disponibilidad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    psicologo_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    motivo VARCHAR(255),
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_excepcion_psicologo_fecha UNIQUE (psicologo_id, fecha)
);

CREATE INDEX IF NOT EXISTS ix_excepcion_psicologo_fecha
    ON citas_schema.excepciones_disponibilidad (psicologo_id, fecha);

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
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_citas_estado CHECK (estado IN ('PENDIENTE','CONFIRMADA','REPROGRAMADA','CANCELADA','COMPLETADA','NO_ASISTIDA')),
    CONSTRAINT ck_citas_modalidad CHECK (modalidad IN ('VIRTUAL','PRESENCIAL')),
    CONSTRAINT ck_citas_rango_fecha CHECK (fecha_hora_fin > fecha_hora_inicio)
);

CREATE INDEX IF NOT EXISTS ix_citas_psicologo_inicio
    ON citas_schema.citas (psicologo_id, fecha_hora_inicio);
CREATE INDEX IF NOT EXISTS ix_citas_paciente_inicio
    ON citas_schema.citas (paciente_id, fecha_hora_inicio);
CREATE INDEX IF NOT EXISTS ix_citas_estado
    ON citas_schema.citas (estado);

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

CREATE INDEX IF NOT EXISTS ix_historial_cita_fecha
    ON citas_schema.historial_cambios_citas (cita_id, fecha_cambio);

-- Servicio de teleconsulta
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

-- Servicio de pagos
CREATE TABLE IF NOT EXISTS pagos_schema.pagos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,
    monto NUMERIC(12,2) NOT NULL,
    moneda VARCHAR(10) NOT NULL DEFAULT 'USD',
    estado VARCHAR(60) NOT NULL DEFAULT 'pendiente',
    creado_en TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pagos_schema.transacciones (
    id SERIAL PRIMARY KEY,
    pago_id INTEGER NOT NULL,
    proveedor VARCHAR(80) NOT NULL,
    proveedor_id VARCHAR(255),
    monto NUMERIC(12,2),
    estado VARCHAR(80) NOT NULL,
    registrado_en TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pagos_schema.comprobantes (
    id SERIAL PRIMARY KEY,
    pago_id INTEGER NOT NULL,
    url_comprobante TEXT,
    creado_en TIMESTAMP NOT NULL DEFAULT NOW()
);