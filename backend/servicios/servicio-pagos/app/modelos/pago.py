import os
import uuid

from sqlalchemy import CheckConstraint, Index
from sqlalchemy.types import Uuid

from app import db
from app.utilidades.tiempo import ahora_utc


DB_SCHEMA = os.getenv("DB_SCHEMA") or os.getenv("DATABASE_SCHEMA") or None

ESTADOS_PAGO = (
    "PENDIENTE",
    "CHECKOUT_ABIERTO",
    "PROCESANDO",
    "PAGADO",
    "FALLIDO",
    "EXPIRADO",
    "CANCELADO",
    "REEMBOLSO_PENDIENTE",
    "REEMBOLSO_PARCIAL",
    "REEMBOLSADO",
    "REPROGRAMACION_PENDIENTE",
    "DISPUTADO",
)


class Pago(db.Model):
    __tablename__ = "pagos"
    _reglas = (
        CheckConstraint(
            "estado IN ('PENDIENTE','CHECKOUT_ABIERTO','PROCESANDO','PAGADO','FALLIDO','EXPIRADO','CANCELADO','REEMBOLSO_PENDIENTE','REEMBOLSO_PARCIAL','REEMBOLSADO','REPROGRAMACION_PENDIENTE','DISPUTADO')",
            name="ck_pagos_estado",
        ),
        CheckConstraint("monto_centavos > 0", name="ck_pagos_monto_positivo"),
        CheckConstraint("reembolsado_centavos >= 0", name="ck_pagos_reembolso_no_negativo"),
        CheckConstraint("reembolsado_centavos <= monto_centavos", name="ck_pagos_reembolso_limite"),
        Index("ix_pagos_paciente_creado", "paciente_id", "creado_en"),
        Index("ix_pagos_psicologo_creado", "psicologo_id", "creado_en"),
        Index("ix_pagos_estado", "estado"),
    )
    __table_args__ = (*_reglas, {"schema": DB_SCHEMA}) if DB_SCHEMA else _reglas

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cita_id = db.Column(Uuid(as_uuid=True), nullable=False, unique=True, index=True)
    paciente_id = db.Column(db.Integer, nullable=False)
    psicologo_id = db.Column(db.Integer, nullable=False)
    monto_centavos = db.Column(db.Integer, nullable=False)
    moneda = db.Column(db.String(3), nullable=False, default="USD")
    estado = db.Column(db.String(32), nullable=False, default="PENDIENTE")
    proveedor = db.Column(db.String(20), nullable=False, default="STRIPE")
    modalidad = db.Column(db.String(15), nullable=False, default="VIRTUAL")
    fecha_hora_inicio = db.Column(db.DateTime(timezone=True), nullable=False)
    fecha_hora_fin = db.Column(db.DateTime(timezone=True), nullable=False)

    stripe_checkout_session_id = db.Column(db.String(255), unique=True)
    stripe_payment_intent_id = db.Column(db.String(255), unique=True)
    stripe_customer_id = db.Column(db.String(255))
    checkout_url = db.Column(db.Text)
    checkout_expira_en = db.Column(db.DateTime(timezone=True))
    comprobante_url = db.Column(db.Text)

    reembolsado_centavos = db.Column(db.Integer, nullable=False, default=0)
    ultimo_error = db.Column(db.Text)
    pagado_en = db.Column(db.DateTime(timezone=True))
    cancelado_en = db.Column(db.DateTime(timezone=True))
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    actualizado_en = db.Column(
        db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc
    )

    transacciones = db.relationship(
        "TransaccionPago",
        back_populates="pago",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    reembolsos = db.relationship(
        "Reembolso",
        back_populates="pago",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def saldo_reembolsable_centavos(self):
        return max(0, int(self.monto_centavos) - int(self.reembolsado_centavos or 0))
