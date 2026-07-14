import os
import uuid

from sqlalchemy import Index
from sqlalchemy.types import Uuid

from app import db
from app.utilidades.tiempo import ahora_utc


DB_SCHEMA = os.getenv("DB_SCHEMA") or None


class HistorialCambioCita(db.Model):
    __tablename__ = "historial_cambios_citas"
    _reglas = (Index("ix_historial_cita_fecha", "cita_id", "fecha_cambio"),)
    __table_args__ = (*_reglas, {"schema": DB_SCHEMA}) if DB_SCHEMA else _reglas

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cita_id = db.Column(Uuid(as_uuid=True), nullable=False)
    accion = db.Column(db.String(40), nullable=False, default="CAMBIO_ESTADO")
    estado_anterior = db.Column(db.String(20))
    estado_nuevo = db.Column(db.String(20), nullable=False)
    cambiado_por = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.Text)
    datos_anteriores = db.Column(db.JSON)
    datos_nuevos = db.Column(db.JSON)
    fecha_cambio = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
