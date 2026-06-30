# Archivo: intentos_login.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

from math import ceil
from threading import Lock
from time import time

from flask import current_app


_LOCK = Lock()


class TooManyLoginAttemptsError(Exception):
    def __init__(self, retry_after, message=None):
        self.retry_after = retry_after
        self.message = message or "Demasiados intentos fallidos. Intenta nuevamente más tarde."
        super().__init__(self.message)


def _key(ip_address, email):
    return f"{ip_address or 'unknown'}:{email.strip().lower()}"


def _config():
    return (
        current_app.config["LOGIN_MAX_ATTEMPTS"],
        current_app.config["LOGIN_ATTEMPT_WINDOW_SECONDS"],
    )


def ensure_login_allowed(ip_address, email):
    key = _key(ip_address, email)
    now = time()
    with _LOCK:
        store = current_app.extensions.setdefault("login_attempts", {})
        # Limpiar intentos anteriores a 10 minutos (600 segundos)
        attempts = [t for t in store.get(key, []) if now - t < 600]
        if attempts:
            store[key] = attempts
        else:
            store.pop(key, None)
            return

        num_fallos = len(attempts)
        if num_fallos == 2:
            ultimo = attempts[-1]
            if now - ultimo < 120:
                restante = ceil(120 - (now - ultimo))
                raise TooManyLoginAttemptsError(
                    restante,
                    f"Tu cuenta ha sido bloqueada temporalmente por seguridad. Podrás intentar de nuevo en {restante} segundos."
                )
        elif num_fallos >= 3:
            ultimo = attempts[-1]
            if now - ultimo < 600:
                restante = ceil(600 - (now - ultimo))
                minutos = ceil(restante / 60)
                raise TooManyLoginAttemptsError(
                    restante,
                    f"Tu cuenta ha sido bloqueada por 10 minutos por seguridad. Podrás intentar de nuevo en {minutos} minutos."
                )


def register_failed_login(ip_address, email):
    key = _key(ip_address, email)
    now = time()
    with _LOCK:
        store = current_app.extensions.setdefault("login_attempts", {})
        attempts = [t for t in store.get(key, []) if now - t < 600]
        attempts.append(now)
        store[key] = attempts


def clear_login_attempts(ip_address, email):
    with _LOCK:
        current_app.extensions.setdefault("login_attempts", {}).pop(
            _key(ip_address, email),
            None,
        )


def unlock_user_login(email):
    email_suffix = f":{email.strip().lower()}"
    with _LOCK:
        store = current_app.extensions.setdefault("login_attempts", {})
        keys_to_delete = [k for k in store.keys() if k.endswith(email_suffix)]
        for k in keys_to_delete:
            store.pop(k, None)
