import os
import uuid

from sqlalchemy import CheckConstraint, Index
from sqlalchemy.types import Uuid

from app import db
from app.utilidades.tiempo import ahora_utc


DB_SCHEMA = os.getenv("DB_SCHEMA") or os.getenv("DATABASE_SCHEMA") or None


class Tarifa(db.Model):
    __tablename__ = "tarifas"
    _reglas = (
        CheckConstraint("modalidad IN ('TODAS','VIRTUAL','PRESENCIAL')", name="ck_tarifas_modalidad"),
        CheckConstraint("monto_centavos > 0", name="ck_tarifas_monto_positivo"),
        Index("ix_tarifas_busqueda", "psicologo_id", "modalidad", "activa", "creado_en"),
    )
    __table_args__ = (*_reglas, {"schema": DB_SCHEMA}) if DB_SCHEMA else _reglas

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    psicologo_id = db.Column(db.Integer)
    modalidad = db.Column(db.String(15), nullable=False, default="TODAS")
    monto_centavos = db.Column(db.Integer, nullable=False)
    moneda = db.Column(db.String(3), nullable=False, default="USD")
    activa = db.Column(db.Boolean, nullable=False, default=True)
    creado_por = db.Column(db.Integer)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    actualizado_en = db.Column(
        db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc
    )
