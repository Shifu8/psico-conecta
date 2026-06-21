import json

from aplicacion.extensiones import db
from aplicacion.modelos.schema import obtener_schema
from aplicacion.utilidades.tiempo import utc_now

_SCHEMA = obtener_schema()


class AuditEvent(db.Model):
    __tablename__ = "eventos_auditoria"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(80), nullable=False, index=True)
    category = db.Column(db.String(40), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="success", index=True)
    actor_user_id = db.Column(db.Integer, nullable=True, index=True)
    target_user_id = db.Column(db.Integer, nullable=True, index=True)
    actor_email = db.Column(db.String(255), nullable=True)
    target_email = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    detail = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)

    def detail_dict(self):
        if not self.detail:
            return {}
        try:
            return json.loads(self.detail)
        except (TypeError, ValueError):
            return {"valor": self.detail}

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "category": self.category,
            "status": self.status,
            "actor_user_id": self.actor_user_id,
            "target_user_id": self.target_user_id,
            "actor_email": self.actor_email,
            "target_email": self.target_email,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "detail": self.detail_dict(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
