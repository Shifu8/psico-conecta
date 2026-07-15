import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.pop("DB_SCHEMA", None)
os.environ.pop("DATABASE_SCHEMA", None)

from flask_jwt_extended import create_access_token

from app import create_app, db


class StripeFalso:
    def __init__(self):
        self.checkout_creados = []
        self.checkout_expirados = []
        self.reembolsos = []
        self.contador_checkout = 0
        self.contador_reembolso = 0

    def crear_checkout(self, parametros, idempotency_key):
        self.contador_checkout += 1
        session_id = f"cs_test_{self.contador_checkout}"
        payment_intent_id = f"pi_test_{self.contador_checkout}"
        sesion = {
            "id": session_id,
            "url": f"https://checkout.stripe.test/{session_id}",
            "status": "open",
            "payment_status": "unpaid",
            "payment_intent": payment_intent_id,
            "customer": f"cus_test_{self.contador_checkout}",
            "amount_total": parametros["line_items"][0]["price_data"]["unit_amount"],
            "metadata": parametros["metadata"],
        }
        self.checkout_creados.append(
            {
                "sesion": sesion,
                "parametros": parametros,
                "idempotency_key": idempotency_key,
            }
        )
        return sesion.copy()

    def obtener_checkout(self, session_id):
        creado = next(
            item["sesion"] for item in self.checkout_creados if item["sesion"]["id"] == session_id
        )
        return {
            **creado,
            "status": "complete",
            "payment_status": "paid",
            "payment_intent": {
                "id": creado["payment_intent"],
                "latest_charge": {
                    "id": f"ch_{session_id}",
                    "receipt_url": f"https://pay.stripe.test/receipts/{session_id}",
                },
            },
        }

    def expirar_checkout(self, session_id):
        self.checkout_expirados.append(session_id)
        return {"id": session_id, "status": "expired"}

    def crear_reembolso(
        self,
        payment_intent_id,
        monto_centavos,
        razon,
        metadata,
        idempotency_key,
    ):
        self.contador_reembolso += 1
        respuesta = {
            "id": f"re_test_{self.contador_reembolso}",
            "status": "succeeded",
            "amount": int(monto_centavos),
            "payment_intent": payment_intent_id,
            "reason": razon,
            "metadata": metadata,
        }
        self.reembolsos.append(
            {
                "respuesta": respuesta,
                "idempotency_key": idempotency_key,
            }
        )
        return respuesta.copy()

    @staticmethod
    def construir_evento(payload, _firma, _secreto):
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        return json.loads(payload)


@pytest.fixture()
def app(tmp_path):
    archivo = tmp_path / "pagos_test.db"
    app = create_app(
        test_config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{archivo}",
            "JWT_SECRET_KEY": "test-secret-key-with-more-than-32-characters",
            "VALIDAR_USUARIO_REMOTO": False,
            "CORS_ORIGINS": ["http://localhost:5173"],
            "INTERNAL_SERVICE_TOKEN": "payments-internal-test-token",
            "STRIPE_SECRET_KEY": "sk_test_fake",
            "STRIPE_WEBHOOK_SECRET": "whsec_test",
            "FRONTEND_URL": "http://localhost:5173",
            "DEFAULT_CONSULTATION_PRICE_CENTS": 3000,
            "DEFAULT_CURRENCY": "USD",
            "CHECKOUT_EXPIRES_MINUTES": 30,
            "AUTO_REFUND_ON_CANCEL": True,
        }
    )
    stripe_falso = StripeFalso()
    app.extensions["stripe_client"] = stripe_falso
    app.stripe_falso = stripe_falso
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def cliente(app):
    return app.test_client()


@pytest.fixture()
def token(app):
    def crear(usuario_id, rol):
        with app.app_context():
            return create_access_token(
                identity=str(usuario_id),
                additional_claims={"role": rol},
            )

    return crear


@pytest.fixture()
def cita_confirmada():
    inicio = datetime.now(timezone.utc) + timedelta(days=3)
    return {
        "id": "a735d0a6-01ab-4ca2-9be4-5d9c0ff4b7b0",
        "paciente_id": 20,
        "psicologo_id": 10,
        "fecha_hora_inicio": inicio.isoformat(),
        "fecha_hora_fin": (inicio + timedelta(minutes=50)).isoformat(),
        "estado": "CONFIRMADA",
        "modalidad": "VIRTUAL",
        "reprogramada_desde": None,
    }


@pytest.fixture()
def sincronizar_cita(cliente):
    def ejecutar(cita, actor_id=10):
        return cliente.post(
            "/api/pagos/interna/citas/sincronizar",
            json={"cita": cita, "actor_id": actor_id},
            headers={"X-Internal-Token": "payments-internal-test-token"},
        )

    return ejecutar
