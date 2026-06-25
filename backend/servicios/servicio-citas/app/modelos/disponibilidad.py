# Archivo: disponibilidad.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Citas

from app import db
import uuid
from datetime import datetime
import os
from sqlalchemy.types import Uuid

DB_SCHEMA = os.getenv("DB_SCHEMA") or None

class Disponibilidad(db.Model):
    __tablename__ = 'disponibilidad'
    if DB_SCHEMA:
        __table_args__ = {'schema': DB_SCHEMA}

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    psicologo_id = db.Column(db.Integer, nullable=False)
    dia_semana = db.Column(db.SmallInteger, nullable=False) # 0=Lunes, 6=Domingo
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    duracion_slot = db.Column(db.SmallInteger, default=50)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=lambda: datetime.utcnow())
    fecha_actualizacion = db.Column(db.DateTime(timezone=True), default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())

class ExcepcionDisponibilidad(db.Model):
    __tablename__ = 'excepciones_disponibilidad'
    if DB_SCHEMA:
        __table_args__ = {'schema': DB_SCHEMA}

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    psicologo_id = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=lambda: datetime.utcnow())
