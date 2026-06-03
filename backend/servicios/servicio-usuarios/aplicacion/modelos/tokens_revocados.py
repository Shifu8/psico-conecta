import os

from aplicacion.extensiones import db
from aplicacion.utilidades.tiempo import utc_now

_SCHEMA = os.environ.get("DATABASE_SCHEMA", "usuarios_schema") or None


class TokenBlocklist(db.Model):
    __tablename__ = "tokens_revocados"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(64), unique=True, nullable=False, index=True)
    revoked_at = db.Column(db.DateTime, nullable=False, default=utc_now)

