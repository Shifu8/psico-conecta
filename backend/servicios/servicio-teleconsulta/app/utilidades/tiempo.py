from datetime import datetime, timezone


def ahora_utc():
    return datetime.now(timezone.utc)


def asegurar_utc(valor):
    if valor is None:
        return None
    if isinstance(valor, str):
        valor = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


def iso_zoom(valor):
    return asegurar_utc(valor).replace(microsecond=0).isoformat().replace("+00:00", "Z")
