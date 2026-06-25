# Archivo: servicio_captcha.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import current_app


TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def captcha_configurado():
    if current_app.config.get("CAPTCHA_DESACTIVADO"):
        return False
    return bool(current_app.config.get("TURNSTILE_SECRET_KEY"))


def verificar_captcha(token, ip_remota=None):
    if current_app.config.get("CAPTCHA_DESACTIVADO"):
        return
    secret = current_app.config.get("TURNSTILE_SECRET_KEY", "")
    if not secret:
        return
    if isinstance(token, str):
        token = token.strip()
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
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    request.add_header("Accept", "application/json")
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
