from flask import current_app
from google.auth.transport import requests
from google.oauth2 import id_token

from aplicacion.extensiones import db
from aplicacion.modelos import Role, User
from aplicacion.utilidades.seguridad import hash_password
from flask_jwt_extended import create_access_token


def _client_id():
    return current_app.config.get(
        "GOOGLE_LOGIN_CLIENT_ID",
        current_app.config.get("GOOGLE_CLIENT_ID", ""),
    )


def verificar_token_google(token):
    try:
        info = id_token.verify_oauth2_token(
            token, requests.Request(), _client_id()
        )
        if info.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            return None
        return info
    except Exception as e:
        current_app.logger.error("Google token verification failed: %s", str(e))
        return None


def google_login(token):
    info = verificar_token_google(token)
    if not info:
        raise ValueError("El token de Google no es valido.")

    email = info.get("email", "").strip().lower()
    google_id = info.get("sub")
    first_name = info.get("given_name", "")
    last_name = info.get("family_name", "")
    if not last_name:
        last_name = info.get("name", "Usuario Google")

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
            password_hash=hash_password(google_id or token[:32]),
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
