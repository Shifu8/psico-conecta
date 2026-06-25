# Archivo: historial.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Citas

from app import db
import uuid
from datetime import datetime
import os
from sqlalchemy.types import Uuid

DB_SCHEMA = os.getenv("DB_SCHEMA") or None

class HistorialCambioCita(db.Model):
    __tablename__ = 'historial_cambios_citas'
    if DB_SCHEMA:
        __table_args__ = {'schema': DB_SCHEMA}

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cita_id = db.Column(Uuid(as_uuid=True), nullable=False)
    estado_anterior = db.Column(db.String(20))
    estado_nuevo = db.Column(db.String(20), nullable=False)
    cambiado_por = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.Text)
    fecha_cambio = db.Column(db.DateTime(timezone=True), default=lambda: datetime.utcnow())
