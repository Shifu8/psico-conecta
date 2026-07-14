import os
import uuid

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlalchemy.types import Uuid

from app import db
from app.utilidades.tiempo import ahora_utc


DB_SCHEMA = os.getenv("DB_SCHEMA") or None


class Disponibilidad(db.Model):
    __tablename__ = "disponibilidad"
    _reglas = (
        CheckConstraint("dia_semana BETWEEN 0 AND 6", name="ck_disponibilidad_dia"),
        CheckConstraint("hora_fin > hora_inicio", name="ck_disponibilidad_horas"),
        CheckConstraint(
            "duracion_slot BETWEEN 15 AND 180", name="ck_disponibilidad_duracion"
        ),
        UniqueConstraint(
            "psicologo_id", "dia_semana", "hora_inicio", "hora_fin",
            name="uq_disponibilidad_bloque",
        ),
        Index("ix_disponibilidad_psicologo_dia", "psicologo_id", "dia_semana"),
    )
    __table_args__ = (*_reglas, {"schema": DB_SCHEMA}) if DB_SCHEMA else _reglas

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    psicologo_id = db.Column(db.Integer, nullable=False)
    dia_semana = db.Column(db.SmallInteger, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    duracion_slot = db.Column(db.SmallInteger, nullable=False, default=50)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    fecha_actualizacion = db.Column(
        db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc
    )


class ExcepcionDisponibilidad(db.Model):
    __tablename__ = "excepciones_disponibilidad"
    _reglas = (
        UniqueConstraint(
            "psicologo_id", "fecha", name="uq_excepcion_psicologo_fecha"
        ),
        Index("ix_excepcion_psicologo_fecha", "psicologo_id", "fecha"),
    )
    __table_args__ = (*_reglas, {"schema": DB_SCHEMA}) if DB_SCHEMA else _reglas

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    psicologo_id = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
