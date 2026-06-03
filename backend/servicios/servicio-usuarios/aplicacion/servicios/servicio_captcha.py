import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import current_app


TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def captcha_configurado():
    return bool(current_app.config.get("TURNSTILE_SECRET_KEY"))


def verificar_captcha(token, ip_remota=None):
    secret = current_app.config.get("TURNSTILE_SECRET_KEY", "")
    if not secret:
        return
    if not token:
        raise ValueError("Completa la verificación de seguridad.")

    payload = {
        "secret": secret,
        "response": token,
    }
    if ip_remota:
        payload["remoteip"] = ip_remota

    data = urlencode(payload).encode("utf-8")
    request = Request(TURNSTILE_VERIFY_URL, data=data, method="POST")
    try:
        with urlopen(request, timeout=8) as response:
            resultado = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        current_app.logger.warning(
            "No se pudo verificar Turnstile: %s", type(error).__name__
        )
        raise ValueError("No se pudo validar la verificación de seguridad.") from None

    if not resultado.get("success"):
        current_app.logger.warning(
            "Turnstile rechazado: %s", resultado.get("error-codes", [])
        )
        raise ValueError("La verificación de seguridad no es válida.")
