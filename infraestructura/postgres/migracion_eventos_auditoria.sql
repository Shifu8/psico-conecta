CREATE SCHEMA IF NOT EXISTS usuarios_schema;

CREATE TABLE IF NOT EXISTS usuarios_schema.eventos_auditoria (
  id SERIAL PRIMARY KEY,
  event_type VARCHAR(80) NOT NULL,
  category VARCHAR(40) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'success',
  actor_user_id INTEGER,
  target_user_id INTEGER,
  actor_email VARCHAR(255),
  target_email VARCHAR(255),
  ip_address VARCHAR(64),
  user_agent VARCHAR(255),
  detail TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_eventos_auditoria_event_type
  ON usuarios_schema.eventos_auditoria (event_type);

CREATE INDEX IF NOT EXISTS ix_eventos_auditoria_category
  ON usuarios_schema.eventos_auditoria (category);

CREATE INDEX IF NOT EXISTS ix_eventos_auditoria_status
  ON usuarios_schema.eventos_auditoria (status);

CREATE INDEX IF NOT EXISTS ix_eventos_auditoria_actor_user_id
  ON usuarios_schema.eventos_auditoria (actor_user_id);

CREATE INDEX IF NOT EXISTS ix_eventos_auditoria_target_user_id
  ON usuarios_schema.eventos_auditoria (target_user_id);

CREATE INDEX IF NOT EXISTS ix_eventos_auditoria_created_at
  ON usuarios_schema.eventos_auditoria (created_at);
