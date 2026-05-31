from aplicacion.extensiones import db
from aplicacion.utilidades.tiempo import utc_now


class TokenBlocklist(db.Model):
    __tablename__ = "tokens_revocados"
    __table_args__ = {"schema": "usuarios_schema"}

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(64), unique=True, nullable=False, index=True)
    revoked_at = db.Column(db.DateTime, nullable=False, default=utc_now)

