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
CREATE TABLE IF NOT EXISTS citas_schema.citas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER,
    psicologo_id INTEGER,
    fecha TIMESTAMP NOT NULL,
    estado VARCHAR(40) NOT NULL DEFAULT 'pendiente',
    descripcion TEXT,
    creado_en TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS citas_schema.horarios_disponibles (
    id SERIAL PRIMARY KEY,
    psicologo_id INTEGER NOT NULL,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS citas_schema.historial_citas (
    id SERIAL PRIMARY KEY,
    cita_id INTEGER NOT NULL,
    evento VARCHAR(255) NOT NULL,
    detalle TEXT,
    registrado_en TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Servicio de teleconsulta
CREATE TABLE IF NOT EXISTS teleconsulta_schema.sesiones_zoom (
    id SERIAL PRIMARY KEY,
    cita_id INTEGER,
    zoom_meeting_id VARCHAR(255),
    tema VARCHAR(255),
    enlace_acceso TEXT,
    estado VARCHAR(60) NOT NULL DEFAULT 'pendiente',
    creado_en TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS teleconsulta_schema.historial_sesiones (
    id SERIAL PRIMARY KEY,
    sesion_id INTEGER NOT NULL,
    evento VARCHAR(255) NOT NULL,
    data JSONB,
    registrado_en TIMESTAMP NOT NULL DEFAULT NOW()
);

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
