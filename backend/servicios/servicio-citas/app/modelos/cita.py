import os
import uuid

from sqlalchemy import CheckConstraint, Index
from sqlalchemy.types import Uuid

from app import db
from app.utilidades.tiempo import ahora_utc


DB_SCHEMA = os.getenv("DB_SCHEMA") or None


class Cita(db.Model):
    __tablename__ = "citas"
    _reglas = (
        CheckConstraint(
            "estado IN ('PENDIENTE','CONFIRMADA','REPROGRAMADA','CANCELADA','COMPLETADA','NO_ASISTIDA')",
            name="ck_citas_estado",
        ),
        CheckConstraint(
            "modalidad IN ('VIRTUAL','PRESENCIAL')",
            name="ck_citas_modalidad",
        ),
        CheckConstraint("fecha_hora_fin > fecha_hora_inicio", name="ck_citas_rango_fecha"),
        Index("ix_citas_psicologo_inicio", "psicologo_id", "fecha_hora_inicio"),
        Index("ix_citas_paciente_inicio", "paciente_id", "fecha_hora_inicio"),
        Index("ix_citas_estado", "estado"),
    )
    __table_args__ = (*_reglas, {"schema": DB_SCHEMA}) if DB_SCHEMA else _reglas

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = db.Column(db.Integer, nullable=False)
    psicologo_id = db.Column(db.Integer, nullable=False)
    fecha_hora_inicio = db.Column(db.DateTime(timezone=True), nullable=False)
    fecha_hora_fin = db.Column(db.DateTime(timezone=True), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="PENDIENTE")
    modalidad = db.Column(db.String(15), nullable=False, default="VIRTUAL")
    motivo_consulta = db.Column(db.Text)
    notas_psicologo = db.Column(db.Text)
    motivo_cancelacion = db.Column(db.Text)
    cancelado_por = db.Column(db.Integer)
    reprogramada_desde = db.Column(Uuid(as_uuid=True))
    fecha_creacion = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    fecha_actualizacion = db.Column(
        db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc
    )
