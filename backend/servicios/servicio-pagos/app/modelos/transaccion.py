import os
import uuid

from sqlalchemy import Index
from sqlalchemy.types import Uuid

from app import db
from app.utilidades.tiempo import ahora_utc


DB_SCHEMA = os.getenv("DB_SCHEMA") or os.getenv("DATABASE_SCHEMA") or None


class TransaccionPago(db.Model):
    __tablename__ = "transacciones"
    _reglas = (Index("ix_transacciones_pago_fecha", "pago_id", "registrado_en"),)
    __table_args__ = (*_reglas, {"schema": DB_SCHEMA}) if DB_SCHEMA else _reglas

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pago_id = db.Column(
        Uuid(as_uuid=True),
        db.ForeignKey(f"{DB_SCHEMA + '.' if DB_SCHEMA else ''}pagos.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo = db.Column(db.String(80), nullable=False)
    estado = db.Column(db.String(40), nullable=False)
    monto_centavos = db.Column(db.Integer)
    proveedor_evento_id = db.Column(db.String(255), unique=True)
    datos = db.Column(db.JSON)
    registrado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)

    pago = db.relationship("Pago", back_populates="transacciones")
