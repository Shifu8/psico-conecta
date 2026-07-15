import os
import uuid

from sqlalchemy import CheckConstraint, Index
from sqlalchemy.types import Uuid

from app import db
from app.utilidades.tiempo import ahora_utc


DB_SCHEMA = os.getenv("DB_SCHEMA") or os.getenv("DATABASE_SCHEMA") or None


class Reembolso(db.Model):
    __tablename__ = "reembolsos"
    _reglas = (
        CheckConstraint(
            "estado IN ('PENDIENTE','PROCESANDO','EXITOSO','FALLIDO','CANCELADO')",
            name="ck_reembolsos_estado",
        ),
        CheckConstraint("monto_centavos > 0", name="ck_reembolsos_monto_positivo"),
        Index("ix_reembolsos_pago_fecha", "pago_id", "creado_en"),
    )
    __table_args__ = (*_reglas, {"schema": DB_SCHEMA}) if DB_SCHEMA else _reglas

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pago_id = db.Column(
        Uuid(as_uuid=True),
        db.ForeignKey(f"{DB_SCHEMA + '.' if DB_SCHEMA else ''}pagos.id", ondelete="CASCADE"),
        nullable=False,
    )
    solicitado_por = db.Column(db.Integer)
    monto_centavos = db.Column(db.Integer, nullable=False)
    razon = db.Column(db.String(40), nullable=False, default="requested_by_customer")
    nota = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default="PENDIENTE")
    stripe_refund_id = db.Column(db.String(255), unique=True)
    ultimo_error = db.Column(db.Text)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    actualizado_en = db.Column(
        db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc
    )

    pago = db.relationship("Pago", back_populates="reembolsos")
