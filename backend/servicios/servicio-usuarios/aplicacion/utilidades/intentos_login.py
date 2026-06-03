from math import ceil
from threading import Lock
from time import time

from flask import current_app


_LOCK = Lock()


class TooManyLoginAttemptsError(Exception):
    def __init__(self, retry_after):
        self.retry_after = retry_after
        super().__init__(
            "Demasiados intentos fallidos. Intenta nuevamente en unos minutos."
        )


def _key(ip_address, email):
    return f"{ip_address or 'unknown'}:{email.strip().lower()}"


def _config():
    return (
        current_app.config["LOGIN_MAX_ATTEMPTS"],
        current_app.config["LOGIN_ATTEMPT_WINDOW_SECONDS"],
    )


def _active_attempts(store, key, now, window):
    attempts = [
        timestamp for timestamp in store.get(key, []) if now - timestamp < window
    ]
    if attempts:
        store[key] = attempts
    else:
        store.pop(key, None)
    return attempts


def ensure_login_allowed(ip_address, email):
    max_attempts, window = _config()
    key = _key(ip_address, email)
    now = time()
    with _LOCK:
        attempts = _active_attempts(
            current_app.extensions.setdefault("login_attempts", {}),
            key,
            now,
            window,
        )
        if len(attempts) >= max_attempts:
            raise TooManyLoginAttemptsError(
                max(1, ceil(window - (now - attempts[0])))
            )


def register_failed_login(ip_address, email):
    _, window = _config()
    key = _key(ip_address, email)
    now = time()
    with _LOCK:
        store = current_app.extensions.setdefault("login_attempts", {})
        attempts = _active_attempts(store, key, now, window)
        attempts.append(now)
        store[key] = attempts


def clear_login_attempts(ip_address, email):
    with _LOCK:
        current_app.extensions.setdefault("login_attempts", {}).pop(
            _key(ip_address, email),
            None,
        )
