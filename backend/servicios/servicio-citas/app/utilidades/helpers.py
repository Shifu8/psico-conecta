from datetime import datetime, timedelta

from sqlalchemy import text

from app import db
from app.utilidades.tiempo import asegurar_datetime_utc


def generar_slots(hora_inicio, hora_fin, duracion_slot_minutos):
    slots = []
    referencia = datetime(2000, 1, 1)
    actual = datetime.combine(referencia.date(), hora_inicio)
    final = datetime.combine(referencia.date(), hora_fin)
    delta = timedelta(minutes=duracion_slot_minutos)

    while actual + delta <= final:
        siguiente = actual + delta
        slots.append({
            "hora_inicio": actual.time(),
            "hora_fin": siguiente.time(),
        })
        actual = siguiente
    return slots


def parse_iso_datetime(valor):
    if not isinstance(valor, str):
        return None
    try:
        fecha = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None
    return asegurar_datetime_utc(fecha)


def bloquear_agendas(psicologo_id, paciente_id=None):
    """Serializa cambios de agenda en PostgreSQL para evitar doble reserva."""
    if db.session.get_bind().dialect.name != "postgresql":
        return

    claves = [int(psicologo_id) * 2]
    if paciente_id is not None:
        claves.append(int(paciente_id) * 2 + 1)

    for clave in sorted(set(claves)):
        db.session.execute(
            text("SELECT pg_advisory_xact_lock(:clave)"),
            {"clave": clave},
        )
