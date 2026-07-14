from datetime import datetime, timedelta, timezone

from app import db
from app.modelos.cita import Cita


def cabecera(token):
    return {"Authorization": f"Bearer {token}"}


def inicio(fecha, hora="08:00:00"):
    return f"{fecha.isoformat()}T{hora}"


def test_agendar_y_evitar_doble_reserva(
    cliente, token, disponibilidad, fecha_habil_futura
):
    paciente_1 = token(20, "PATIENT")
    paciente_2 = token(21, "PATIENT")
    datos = {
        "psicologo_id": "10",
        "fecha_hora_inicio": inicio(fecha_habil_futura),
        "modalidad": "VIRTUAL",
        "motivo_consulta": "Consulta inicial",
    }

    respuesta = cliente.post("/api/citas", json=datos, headers=cabecera(paciente_1))
    assert respuesta.status_code == 201
    assert respuesta.json["paciente_id"] == 20
    assert respuesta.json["estado"] == "PENDIENTE"

    duplicada = cliente.post("/api/citas", json=datos, headers=cabecera(paciente_2))
    assert duplicada.status_code == 409
    assert duplicada.json["error"] == "horario_ocupado"


def test_confirmar_reprogramar_e_historial(
    cliente, token, disponibilidad, fecha_habil_futura
):
    paciente = token(20, "PATIENT")
    psicologo = token(10, "PSYCHOLOGIST")
    creada = cliente.post(
        "/api/citas",
        json={
            "psicologo_id": 10,
            "fecha_hora_inicio": inicio(fecha_habil_futura),
            "modalidad": "PRESENCIAL",
        },
        headers=cabecera(paciente),
    )
    cita_id = creada.json["id"]

    confirmada = cliente.put(
        f"/api/citas/{cita_id}/confirmar", headers=cabecera(psicologo)
    )
    assert confirmada.status_code == 200
    assert confirmada.json["estado"] == "CONFIRMADA"

    nueva = cliente.put(
        f"/api/citas/{cita_id}/reprogramar",
        json={"nueva_fecha_hora_inicio": inicio(fecha_habil_futura, "08:50:00")},
        headers=cabecera(paciente),
    )
    assert nueva.status_code == 200
    assert nueva.json["estado"] == "PENDIENTE"
    assert nueva.json["reprogramada_desde"] == cita_id

    antigua = cliente.get(f"/api/citas/{cita_id}", headers=cabecera(paciente))
    assert antigua.json["estado"] == "REPROGRAMADA"

    historial = cliente.get(
        f"/api/citas/{cita_id}/historial", headers=cabecera(paciente)
    )
    assert historial.status_code == 200
    assert [evento["accion"] for evento in historial.json] == [
        "CREACION",
        "CONFIRMAR",
        "REPROGRAMAR_ORIGEN",
    ]


def test_bloqueos_de_fecha_solo_administrador(
    cliente, token, disponibilidad, fecha_habil_futura
):
    psicologo = token(10, "PSYCHOLOGIST")
    admin = token(1, "ADMIN")
    datos = {"fecha": fecha_habil_futura.isoformat(), "motivo": "Vacaciones"}

    denegada = cliente.post(
        "/api/disponibilidad/10/excepciones",
        json=datos,
        headers=cabecera(psicologo),
    )
    assert denegada.status_code == 403

    creada = cliente.post(
        "/api/disponibilidad/10/excepciones",
        json=datos,
        headers=cabecera(admin),
    )
    assert creada.status_code == 201

    slots = cliente.get(
        f"/api/disponibilidad/10/slots?fecha={fecha_habil_futura.isoformat()}"
    )
    assert slots.status_code == 200
    assert slots.json["slots"] == []


def test_horario_base_para_psicologo_sin_bloques(cliente, fecha_habil_futura):
    respuesta = cliente.get(
        f"/api/disponibilidad/99/slots?fecha={fecha_habil_futura.isoformat()}"
    )
    assert respuesta.status_code == 200
    assert respuesta.json["slots"]
    assert respuesta.json["slots"][0]["hora_inicio"] == "08:00:00"


def test_completar_y_no_asistida_solo_despues_del_fin(cliente, token, app):
    psicologo = token(10, "PSYCHOLOGIST")
    paciente = token(20, "PATIENT")
    with app.app_context():
        futura = Cita(
            paciente_id=20,
            psicologo_id=10,
            fecha_hora_inicio=datetime.now(timezone.utc) + timedelta(hours=1),
            fecha_hora_fin=datetime.now(timezone.utc) + timedelta(hours=2),
            estado="CONFIRMADA",
            modalidad="VIRTUAL",
        )
        pasada = Cita(
            paciente_id=20,
            psicologo_id=10,
            fecha_hora_inicio=datetime.now(timezone.utc) - timedelta(hours=2),
            fecha_hora_fin=datetime.now(timezone.utc) - timedelta(hours=1),
            estado="CONFIRMADA",
            modalidad="VIRTUAL",
        )
        db.session.add_all([futura, pasada])
        db.session.commit()
        futura_id, pasada_id = str(futura.id), str(pasada.id)

    prematura = cliente.put(
        f"/api/citas/{futura_id}/completar", headers=cabecera(psicologo)
    )
    assert prematura.status_code == 409

    completada = cliente.put(
        f"/api/citas/{pasada_id}/completar", headers=cabecera(psicologo)
    )
    assert completada.status_code == 200
    assert completada.json["estado"] == "COMPLETADA"

    denegada = cliente.get(
        f"/api/citas/{pasada_id}", headers=cabecera(paciente)
    )
    assert denegada.status_code == 200
