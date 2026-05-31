from aplicacion.extensiones import db
from aplicacion.utilidades.tiempo import utc_now


class PasswordResetToken(db.Model):
    __tablename__ = "tokens_recuperacion"
    __table_args__ = {"schema": "usuarios_schema"}

    id = db.Column(db.Integer, primary_key=True)
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("usuarios_schema.usuarios.id"), nullable=False
    )
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship("User", backref=db.backref("password_reset_tokens", lazy=True))

    @property
    def is_active(self):
        return self.used_at is None and self.expires_at > utc_now()

