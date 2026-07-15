import copy
import json
import uuid

from app import db
from app.modelos import Pago


def auth(token, usuario_id, rol):
    return {"Authorization": f"Bearer {token(usuario_id, rol)}"}


def completar_pago(cliente, token, cita, sincronizar_cita):
    respuesta = sincronizar_cita(cita)
    assert respuesta.status_code == 200
    pago = respuesta.get_json()["pago"]

    checkout = cliente.post(
        f"/api/pagos/cita/{cita['id']}/checkout",
        headers=auth(token, cita["paciente_id"], "PATIENT"),
    )
    assert checkout.status_code == 200
    pago = checkout.get_json()["pago"]
    session_id = pago["checkout_url"].rsplit("/", 1)[-1]

    evento = {
        "id": f"evt_{uuid.uuid4().hex}",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": session_id,
                "status": "complete",
                "payment_status": "paid",
                "amount_total": pago["monto_centavos"],
                "payment_intent": f"pi_{session_id}",
                "metadata": {"pago_id": pago["id"], "cita_id": cita["id"]},
            }
        },
    }
    webhook = cliente.post(
        "/api/pagos/webhooks/stripe",
        data=json.dumps(evento),
        headers={"Stripe-Signature": "firma-test", "Content-Type": "application/json"},
    )
    assert webhook.status_code == 200
    return pago["id"], evento


def test_checkout_webhook_idempotente_y_comprobante(
    cliente, token, cita_confirmada, sincronizar_cita, app
):
    creada = sincronizar_cita(cita_confirmada)
    assert creada.status_code == 200
    pago_inicial = creada.get_json()["pago"]
    assert pago_inicial["estado"] == "PENDIENTE"
    assert pago_inicial["monto_centavos"] == 3000

    checkout = cliente.post(
        f"/api/pagos/cita/{cita_confirmada['id']}/checkout",
        headers=auth(token, 20, "PATIENT"),
    )
    assert checkout.status_code == 200
    datos_checkout = checkout.get_json()["pago"]
    assert datos_checkout["estado"] == "CHECKOUT_ABIERTO"
    assert datos_checkout["checkout_url"].startswith("https://checkout.stripe.test/")

    session_id = datos_checkout["checkout_url"].rsplit("/", 1)[-1]
    sincronizada = cliente.post(
        f"/api/pagos/checkout/{session_id}/sincronizar",
        headers=auth(token, 20, "PATIENT"),
    )
    assert sincronizada.status_code == 200
    pago = sincronizada.get_json()["pago"]
    assert pago["estado"] == "PAGADO"
    assert pago["comprobante_url"].endswith(session_id)

    with app.app_context():
        pago_db = Pago.query.filter_by(id=uuid.UUID(pago["id"])).one()
        evento = {
            "id": "evt_checkout_idempotente",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": session_id,
                    "status": "complete",
                    "payment_status": "paid",
                    "amount_total": 3000,
                    "payment_intent": pago_db.stripe_payment_intent_id,
                    "metadata": {"pago_id": str(pago_db.id)},
                }
            },
        }

    primera = cliente.post(
        "/api/pagos/webhooks/stripe",
        data=json.dumps(evento),
        headers={"Stripe-Signature": "firma-test", "Content-Type": "application/json"},
    )
    segunda = cliente.post(
        "/api/pagos/webhooks/stripe",
        data=json.dumps(evento),
        headers={"Stripe-Signature": "firma-test", "Content-Type": "application/json"},
    )
    assert primera.status_code == 200
    assert segunda.status_code == 200
    assert segunda.get_json()["duplicado"] is True


def test_roles_y_ocultamiento_del_enlace(cliente, token, cita_confirmada, sincronizar_cita):
    creada = sincronizar_cita(cita_confirmada).get_json()["pago"]
    cliente.post(
        f"/api/pagos/cita/{cita_confirmada['id']}/checkout",
        headers=auth(token, 20, "PATIENT"),
    )

    paciente_ajeno = cliente.get(
        f"/api/pagos/{creada['id']}",
        headers=auth(token, 99, "PATIENT"),
    )
    assert paciente_ajeno.status_code == 403

    psicologo = cliente.get(
        f"/api/pagos/{creada['id']}",
        headers=auth(token, 10, "PSYCHOLOGIST"),
    )
    assert psicologo.status_code == 200
    assert psicologo.get_json()["pago"]["checkout_url"] is None


def test_tarifa_del_servidor_se_aplica_a_nuevos_pagos(
    cliente, token, cita_confirmada, sincronizar_cita
):
    tarifa = cliente.post(
        "/api/pagos/tarifas",
        json={
            "psicologo_id": 10,
            "modalidad": "VIRTUAL",
            "monto_centavos": 4250,
            "moneda": "USD",
        },
        headers=auth(token, 1, "ADMIN"),
    )
    assert tarifa.status_code == 201

    pago = sincronizar_cita(cita_confirmada).get_json()["pago"]
    assert pago["monto_centavos"] == 4250
    assert pago["monto"] == 42.5


def test_reembolso_parcial_y_total(
    cliente, token, cita_confirmada, sincronizar_cita, app
):
    pago_id, _ = completar_pago(cliente, token, cita_confirmada, sincronizar_cita)

    parcial = cliente.post(
        f"/api/pagos/{pago_id}/reembolsar",
        json={"monto_centavos": 1000, "razon": "requested_by_customer"},
        headers=auth(token, 1, "ADMIN"),
    )
    assert parcial.status_code == 200
    assert parcial.get_json()["pago"]["estado"] == "REEMBOLSO_PARCIAL"
    assert parcial.get_json()["pago"]["saldo_reembolsable_centavos"] == 2000

    total = cliente.post(
        f"/api/pagos/{pago_id}/reembolsar",
        json={"monto_centavos": 2000, "razon": "requested_by_customer"},
        headers=auth(token, 1, "ADMIN"),
    )
    assert total.status_code == 200
    assert total.get_json()["pago"]["estado"] == "REEMBOLSADO"
    assert len(app.stripe_falso.reembolsos) == 2


def test_cancelacion_reembolsa_automaticamente(
    cliente, token, cita_confirmada, sincronizar_cita, app
):
    pago_id, _ = completar_pago(cliente, token, cita_confirmada, sincronizar_cita)
    cancelada = copy.deepcopy(cita_confirmada)
    cancelada["estado"] = "CANCELADA"

    respuesta = sincronizar_cita(cancelada, actor_id=20)
    assert respuesta.status_code == 200
    pago = respuesta.get_json()["pago"]
    assert pago["id"] == pago_id
    assert pago["estado"] == "REEMBOLSADO"
    assert len(app.stripe_falso.reembolsos) == 1


def test_reprogramacion_transfiere_el_pago(
    cliente, token, cita_confirmada, sincronizar_cita
):
    pago_id, _ = completar_pago(cliente, token, cita_confirmada, sincronizar_cita)

    anterior = copy.deepcopy(cita_confirmada)
    anterior["estado"] = "REPROGRAMADA"
    respuesta_anterior = sincronizar_cita(anterior)
    assert respuesta_anterior.status_code == 200
    assert respuesta_anterior.get_json()["pago"]["estado"] == "REPROGRAMACION_PENDIENTE"

    nueva = copy.deepcopy(cita_confirmada)
    nueva["id"] = "59b30a86-0663-42c7-8f53-3e369a29b981"
    nueva["estado"] = "PENDIENTE"
    nueva["reprogramada_desde"] = cita_confirmada["id"]
    respuesta_nueva = sincronizar_cita(nueva)
    assert respuesta_nueva.status_code == 200
    pago = respuesta_nueva.get_json()["pago"]
    assert pago["id"] == pago_id
    assert pago["cita_id"] == nueva["id"]
    assert pago["estado"] == "PAGADO"

    estado_antiguo = cliente.get(
        f"/api/pagos/interna/citas/{cita_confirmada['id']}/estado",
        headers={"X-Internal-Token": "payments-internal-test-token"},
    )
    assert estado_antiguo.get_json()["pago_encontrado"] is False

    estado_nuevo = cliente.get(
        f"/api/pagos/interna/citas/{nueva['id']}/estado",
        headers={"X-Internal-Token": "payments-internal-test-token"},
    )
    assert estado_nuevo.get_json()["pagado"] is True


def test_webhook_revierte_reembolso_que_falla_despues(
    cliente, token, cita_confirmada, sincronizar_cita, app
):
    pago_id, _ = completar_pago(cliente, token, cita_confirmada, sincronizar_cita)
    reembolsado = cliente.post(
        f"/api/pagos/{pago_id}/reembolsar",
        json={"monto_centavos": 1000, "razon": "requested_by_customer"},
        headers=auth(token, 1, "ADMIN"),
    )
    assert reembolsado.status_code == 200
    assert reembolsado.get_json()["pago"]["reembolsado_centavos"] == 1000

    with app.app_context():
        pago = Pago.query.filter_by(id=uuid.UUID(pago_id)).one()
        reembolso = pago.reembolsos[0]
        evento = {
            "id": "evt_refund_failed_after_success",
            "type": "refund.failed",
            "data": {
                "object": {
                    "id": reembolso.stripe_refund_id,
                    "status": "failed",
                    "amount": reembolso.monto_centavos,
                    "failure_reason": "insufficient_funds",
                    "metadata": {
                        "pago_id": str(pago.id),
                        "reembolso_id": str(reembolso.id),
                    },
                }
            },
        }

    respuesta = cliente.post(
        "/api/pagos/webhooks/stripe",
        data=json.dumps(evento),
        headers={"Stripe-Signature": "firma-test", "Content-Type": "application/json"},
    )
    assert respuesta.status_code == 200

    detalle = cliente.get(
        f"/api/pagos/{pago_id}",
        headers=auth(token, 1, "ADMIN"),
    ).get_json()["pago"]
    assert detalle["reembolsado_centavos"] == 0
    assert detalle["estado"] == "PAGADO"
    assert detalle["reembolsos"][0]["estado"] == "FALLIDO"


def test_administrador_sincroniza_citas_confirmadas_existentes(
    cliente, token, cita_confirmada, monkeypatch
):
    from app.servicios.cliente_citas import ClienteCitas

    segunda = copy.deepcopy(cita_confirmada)
    segunda["id"] = "457c45aa-4535-41c4-91bc-38f1db7e5858"
    segunda["paciente_id"] = 21
    monkeypatch.setattr(
        ClienteCitas,
        "listar_citas",
        staticmethod(lambda estado=None: [cita_confirmada, segunda]),
    )

    respuesta = cliente.post(
        "/api/pagos/sincronizar-citas",
        headers=auth(token, 1, "ADMIN"),
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json()["procesadas"] == 2
    assert respuesta.get_json()["creadas_o_actualizadas"] == 2

    listado = cliente.get(
        "/api/pagos",
        headers=auth(token, 1, "ADMIN"),
    )
    assert len(listado.get_json()["pagos"]) == 2
