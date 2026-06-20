from app import db
import uuid
from datetime import datetime
import os
from sqlalchemy.types import Uuid

DB_SCHEMA = os.getenv("DB_SCHEMA") or None

class Cita(db.Model):
    __tablename__ = 'citas'
    if DB_SCHEMA:
        __table_args__ = {'schema': DB_SCHEMA}

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = db.Column(db.Integer, nullable=False)
    psicologo_id = db.Column(db.Integer, nullable=False)
    fecha_hora_inicio = db.Column(db.DateTime(timezone=True), nullable=False)
    fecha_hora_fin = db.Column(db.DateTime(timezone=True), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='PENDIENTE')
    modalidad = db.Column(db.String(15), default='VIRTUAL')
    motivo_consulta = db.Column(db.Text)
    notas_psicologo = db.Column(db.Text)
    motivo_cancelacion = db.Column(db.Text)
    cancelado_por = db.Column(db.Integer)
    reprogramada_desde = db.Column(Uuid(as_uuid=True))
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=lambda: datetime.utcnow())
    fecha_actualizacion = db.Column(db.DateTime(timezone=True), default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())

    # Constraints will be enforced at application level or via DB migrations explicitly
