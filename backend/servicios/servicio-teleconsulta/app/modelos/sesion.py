import os
import uuid

from sqlalchemy import CheckConstraint, Index
from sqlalchemy.types import Uuid

from app import db
from app.utilidades.tiempo import ahora_utc

DB_SCHEMA = os.getenv("DB_SCHEMA") or os.getenv("DATABASE_SCHEMA") or None


class SesionZoom(db.Model):
    __tablename__ = "sesiones_zoom"
    reglas = (
        CheckConstraint(
            "estado IN ('PROGRAMADA','EN_CURSO','FINALIZADA','CANCELADA','ERROR')",
            name="ck_sesiones_zoom_estado",
        ),
        CheckConstraint("fecha_hora_fin > fecha_hora_inicio", name="ck_sesiones_zoom_rango"),
        Index("ix_sesiones_zoom_psicologo_inicio", "psicologo_id", "fecha_hora_inicio"),
        Index("ix_sesiones_zoom_paciente_inicio", "paciente_id", "fecha_hora_inicio"),
        Index("ix_sesiones_zoom_estado", "estado"),
    )
    __table_args__ = (*reglas, {"schema": DB_SCHEMA}) if DB_SCHEMA else reglas

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cita_id = db.Column(Uuid(as_uuid=True), nullable=False, unique=True, index=True)
    paciente_id = db.Column(db.Integer, nullable=False)
    psicologo_id = db.Column(db.Integer, nullable=False)
    zoom_meeting_id = db.Column(db.String(32), unique=True)
    zoom_meeting_uuid = db.Column(db.String(255))
    zoom_host_user_id = db.Column(db.String(255))
    tema = db.Column(db.String(255), nullable=False, default="Teleconsulta PsicoConecta")
    enlace_acceso = db.Column(db.Text)
    contrasena = db.Column(db.String(64))
    fecha_hora_inicio = db.Column(db.DateTime(timezone=True), nullable=False)
    fecha_hora_fin = db.Column(db.DateTime(timezone=True), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="PROGRAMADA")
    ultimo_error = db.Column(db.Text)
    ultima_sincronizacion_zoom = db.Column(db.DateTime(timezone=True))
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    actualizado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc)
