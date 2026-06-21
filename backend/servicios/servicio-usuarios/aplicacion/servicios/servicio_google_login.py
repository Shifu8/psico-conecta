from secrets import token_urlsafe

from flask import current_app
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from aplicacion.extensiones import db
from aplicacion.modelos import Role, User
from aplicacion.utilidades.seguridad import hash_password
from aplicacion.utilidades.validacion import normalize_spaces
from flask_jwt_extended import create_access_token


def _client_ids():
    ids_configurados = (
        current_app.config.get("GOOGLE_LOGIN_CLIENT_ID") or "",
        current_app.config.get("GOOGLE_CLIENT_ID") or "",
    )
    ids = []
    for valor in ids_configurados:
        for cid in str(valor).split(","):
            cid = cid.strip()
            if cid and cid not in ids:
                ids.append(cid)
    return ids


def verificar_token_google(token):
    client_ids = _client_ids()
    if not client_ids:
        raise ValueError("Inicio con Google no configurado. Define GOOGLE_LOGIN_CLIENT_ID.")
    try:
        info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=None,
            clock_skew_in_seconds=60,
        )
        if info.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
            current_app.logger.warning("Google ID token rechazado por emisor inválido.")
            return None
        audience = info.get("aud")
        if audience not in client_ids:
            current_app.logger.warning(
                "Google ID token rechazado por audiencia no permitida. aud=%s permitidos=%s",
                audience,
                ",".join(client_ids),
            )
            raise ValueError(
                "El token de Google no coincide con el Client ID configurado. "
                "Usa el mismo valor en VITE_GOOGLE_CLIENT_ID y GOOGLE_LOGIN_CLIENT_ID."
            )
        return info
    except Exception as error:
        if str(error).startswith("El token de Google no coincide"):
            raise
        current_app.logger.warning(
            "Google ID token rechazado: %s - %s", type(error).__name__, error
        )
    return None


def google_login(token):
    info = verificar_token_google(token)
    if not info:
        raise ValueError("El token de Google no es válido.")

    email = info.get("email", "").strip().lower()
    google_id = info.get("sub")
    if not email or not google_id or info.get("email_verified") is not True:
        raise ValueError("No fue posible validar el correo de tu cuenta de Google.")

    first_name = normalize_spaces(info.get("given_name") or "")[:80]
    last_name = normalize_spaces(info.get("family_name") or "")[:80]
    if not last_name:
        last_name = normalize_spaces(info.get("name") or "Usuario Google")[:80]

    user = User.query.filter_by(email=email).first()

    if user:
        if user.status != "active":
            raise ValueError("Tu cuenta se encuentra inactiva.")
        user.google_id = google_id
    else:
        role = Role.query.filter_by(name="PATIENT").first()
        if not role:
            raise RuntimeError("Ejecuta datos_iniciales.py para crear los roles iniciales.")
        user = User(
            first_name=first_name or "Usuario",
            last_name=last_name or "Google",
            email=email,
            password_hash=hash_password(token_urlsafe(32)),
            google_id=google_id,
            phone=None,
            role=role,
        )
        db.session.add(user)

    db.session.commit()
    access_token = create_access_token(
        identity=str(user.id), additional_claims={"role": user.role.name}
    )
    return user, access_token
