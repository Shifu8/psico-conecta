from datetime import datetime, timezone


def ahora_utc():
    return datetime.now(timezone.utc)


def asegurar_utc(valor):
    if valor is None:
        return None
    if isinstance(valor, str):
        texto = valor.strip().replace("Z", "+00:00")
        valor = datetime.fromisoformat(texto)
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)
