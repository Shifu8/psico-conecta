from aplicacion.extensiones import db
from aplicacion.modelos.schema import obtener_schema
from aplicacion.utilidades.tiempo import utc_now

_SCHEMA = obtener_schema()


class TokenBlocklist(db.Model):
    __tablename__ = "tokens_revocados"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(64), unique=True, nullable=False, index=True)
    revoked_at = db.Column(db.DateTime, nullable=False, default=utc_now)
