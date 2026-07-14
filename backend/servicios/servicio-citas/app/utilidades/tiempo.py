from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from flask import current_app


def ahora_utc():
    return datetime.now(timezone.utc)


def zona_local():
    return ZoneInfo(current_app.config.get("TIMEZONE", "America/Guayaquil"))


def asegurar_datetime_utc(valor, asumir_local_si_naive=True):
    """Devuelve UTC. Entradas del usuario sin zona se interpretan como hora local.

    Los motores como SQLite pueden devolver sin zona valores que originalmente se
    guardaron en UTC; para esos casos usa ``asumir_local_si_naive=False``.
    """
    if valor.tzinfo is None:
        zona = zona_local() if asumir_local_si_naive else timezone.utc
        valor = valor.replace(tzinfo=zona)
    return valor.astimezone(timezone.utc)


def a_hora_local(valor):
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(zona_local())


def combinar_fecha_hora_local(fecha, hora):
    return datetime.combine(fecha, hora).replace(tzinfo=zona_local())


def limites_dia_utc(fecha):
    inicio_local = combinar_fecha_hora_local(fecha, time.min)
    fin_local = combinar_fecha_hora_local(fecha, time.max)
    return inicio_local.astimezone(timezone.utc), fin_local.astimezone(timezone.utc)


def fecha_local_actual():
    return datetime.now(zona_local()).date()
