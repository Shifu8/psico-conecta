import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone

from app import db
from app.modelos import SesionZoom
from app.servicios.cliente_citas import ClienteCitas


def cabecera(token):
    return {"Authorization": f"Bearer {token}"}


def cabecera_interna():
    return {"X-Internal-Token": "internal-test-token"}


def test_confirmacion_crea_reunion_zoom(cliente, app, cita_virtual_confirmada):
    respuesta = cliente.post(
        "/api/teleconsultas/interna/citas/sincronizar",
        json={"actor_id": 10, "cita": cita_virtual_confirmada},
        headers=cabecera_interna(),
    )
    assert respuesta.status_code == 200
    assert respuesta.json["sesion"]["estado"] == "PROGRAMADA"
    assert respuesta.json["sesion"]["zoom_configurada"] is True

    with app.app_context():
        sesion = SesionZoom.query.one()
        assert sesion.cita_id.hex == "a735d0a601ab4ca29be45d9c0ff4b7b0"
        assert sesion.enlace_acceso.startswith("https://zoom.example/j/")
        assert sesion.zoom_host_user_id == "psicologo-10@example.com"
        # El enlace de anfitrión nunca se persiste en la base de datos.
        assert "zak=" not in (sesion.enlace_acceso or "")


def test_acceso_distinto_para_paciente_y_psicologo(
    cliente, token, app, cita_virtual_confirmada, monkeypatch
):
    cliente.post(
        "/api/teleconsultas/interna/citas/sincronizar",
        json={"cita": cita_virtual_confirmada},
        headers=cabecera_interna(),
    )
    monkeypatch.setattr(ClienteCitas, "obtener_cita", staticmethod(lambda _id: cita_virtual_confirmada))

    paciente = cliente.post(
        f"/api/teleconsultas/cita/{cita_virtual_confirmada['id']}/acceso",
        headers=cabecera(token(20, "PATIENT")),
    )
    assert paciente.status_code == 200
    assert "/j/" in paciente.json["url"]
    assert "zak=" not in paciente.json["url"]

    psicologo = cliente.post(
        f"/api/teleconsultas/cita/{cita_virtual_confirmada['id']}/acceso",
        headers=cabecera(token(10, "PSYCHOLOGIST")),
    )
    assert psicologo.status_code == 200
    assert "/s/" in psicologo.json["url"]
    assert "zak=" in psicologo.json["url"]


def test_acceso_no_se_habilita_demasiado_pronto(
    cliente, token, cita_virtual_confirmada, monkeypatch
):
    inicio = datetime.now(timezone.utc) + timedelta(hours=2)
    cita = {
        **cita_virtual_confirmada,
        "fecha_hora_inicio": inicio.isoformat(),
        "fecha_hora_fin": (inicio + timedelta(minutes=50)).isoformat(),
    }
    cliente.post(
        "/api/teleconsultas/interna/citas/sincronizar",
        json={"cita": cita},
        headers=cabecera_interna(),
    )
    monkeypatch.setattr(ClienteCitas, "obtener_cita", staticmethod(lambda _id: cita))

    respuesta = cliente.post(
        f"/api/teleconsultas/cita/{cita['id']}/acceso",
        headers=cabecera(token(20, "PATIENT")),
    )
    assert respuesta.status_code == 403
    assert respuesta.json["error"] == "acceso_fuera_de_horario"
    assert respuesta.json["detalles"]["disponible_desde"]


def test_cancelar_cita_elimina_reunion(cliente, app, cita_virtual_confirmada):
    creada = cliente.post(
        "/api/teleconsultas/interna/citas/sincronizar",
        json={"cita": cita_virtual_confirmada},
        headers=cabecera_interna(),
    )
    meeting_id = next(iter(app.zoom_falso.reuniones))
    cancelada = {**cita_virtual_confirmada, "estado": "CANCELADA"}

    respuesta = cliente.post(
        "/api/teleconsultas/interna/citas/sincronizar",
        json={"actor_id": 20, "cita": cancelada},
        headers=cabecera_interna(),
    )
    assert creada.status_code == 200
    assert respuesta.status_code == 200
    assert respuesta.json["sesion"]["estado"] == "CANCELADA"
    assert meeting_id in app.zoom_falso.eliminadas

    with app.app_context():
        sesion = SesionZoom.query.one()
        assert sesion.zoom_meeting_id is None
        assert sesion.enlace_acceso is None


def test_listado_sincroniza_solo_citas_virtuales(
    cliente, token, cita_virtual_confirmada, monkeypatch
):
    presencial = {
        **cita_virtual_confirmada,
        "id": "784d8850-2523-4b04-b220-0af9890747ab",
        "modalidad": "PRESENCIAL",
    }
    monkeypatch.setattr(
        ClienteCitas,
        "mis_citas",
        staticmethod(lambda: [cita_virtual_confirmada, presencial]),
    )

    respuesta = cliente.get(
        "/api/teleconsultas/mis-sesiones",
        headers=cabecera(token(20, "PATIENT")),
    )
    assert respuesta.status_code == 200
    assert len(respuesta.json) == 1
    assert respuesta.json[0]["cita_id"] == cita_virtual_confirmada["id"]


def test_webhook_valida_endpoint_y_finaliza_reunion(
    cliente, app, cita_virtual_confirmada
):
    cliente.post(
        "/api/teleconsultas/interna/citas/sincronizar",
        json={"cita": cita_virtual_confirmada},
        headers=cabecera_interna(),
    )
    meeting_id = next(iter(app.zoom_falso.reuniones))
    secreto = "webhook-secret"
    app.config["ZOOM_WEBHOOK_SECRET_TOKEN"] = secreto

    validacion = cliente.post(
        "/api/teleconsultas/webhooks/zoom",
        json={"event": "endpoint.url_validation", "payload": {"plainToken": "token-plano"}},
    )
    assert validacion.status_code == 200
    esperado = hmac.new(secreto.encode(), b"token-plano", hashlib.sha256).hexdigest()
    assert validacion.json == {"plainToken": "token-plano", "encryptedToken": esperado}

    evento = {
        "event": "meeting.ended",
        "payload": {"object": {"id": int(meeting_id), "uuid": "uuid-final"}},
    }
    cuerpo = json.dumps(evento, separators=(",", ":")).encode()
    marca = str(int(time.time()))
    firma = "v0=" + hmac.new(
        secreto.encode(), f"v0:{marca}:".encode() + cuerpo, hashlib.sha256
    ).hexdigest()
    terminado = cliente.post(
        "/api/teleconsultas/webhooks/zoom",
        data=cuerpo,
        content_type="application/json",
        headers={"x-zm-request-timestamp": marca, "x-zm-signature": firma},
    )
    assert terminado.status_code == 200

    with app.app_context():
        assert SesionZoom.query.one().estado == "FINALIZADA"
