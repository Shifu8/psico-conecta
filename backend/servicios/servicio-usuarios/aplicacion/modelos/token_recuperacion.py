# Archivo: token_recuperacion.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

from aplicacion.extensiones import db
from aplicacion.modelos.schema import obtener_schema, prefijo_schema
from aplicacion.utilidades.tiempo import utc_now

_SCHEMA = obtener_schema()
_SCHEMA_PREFIX = prefijo_schema(_SCHEMA)


class PasswordResetToken(db.Model):
    __tablename__ = "tokens_recuperacion"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = db.Column(db.Integer, primary_key=True)
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{_SCHEMA_PREFIX}usuarios.id"),
        nullable=False,
    )
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship("User", backref=db.backref("password_reset_tokens", lazy=True))

    @property
    def is_active(self):
        return self.used_at is None and self.expires_at > utc_now()
