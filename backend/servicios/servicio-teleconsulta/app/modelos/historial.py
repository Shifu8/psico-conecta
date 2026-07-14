import os
import uuid

from sqlalchemy import Index
from sqlalchemy.types import Uuid

from app import db
from app.utilidades.tiempo import ahora_utc

DB_SCHEMA = os.getenv("DB_SCHEMA") or os.getenv("DATABASE_SCHEMA") or None
SESION_FK = f"{DB_SCHEMA}.sesiones_zoom.id" if DB_SCHEMA else "sesiones_zoom.id"


class HistorialSesion(db.Model):
    __tablename__ = "historial_sesiones"
    reglas = (Index("ix_historial_sesion_fecha", "sesion_id", "registrado_en"),)
    __table_args__ = (*reglas, {"schema": DB_SCHEMA}) if DB_SCHEMA else reglas

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sesion_id = db.Column(
        Uuid(as_uuid=True),
        db.ForeignKey(SESION_FK, ondelete="CASCADE"),
        nullable=False,
    )
    evento = db.Column(db.String(80), nullable=False)
    actor_id = db.Column(db.Integer)
    data = db.Column(db.JSON)
    registrado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
