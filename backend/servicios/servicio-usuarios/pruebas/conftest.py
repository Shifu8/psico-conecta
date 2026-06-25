# Archivo: conftest.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aplicacion import create_app
from aplicacion.extensiones import db
from datos_iniciales import seed_database


@pytest.fixture()
def app():
    application = create_app(
        {
            "TESTING": True,
            "DEBUG": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "execution_options": {
                    "schema_translate_map": {"usuarios_schema": None},
                },
            },
            "JWT_SECRET_KEY": "test-secret-with-at-least-thirty-two-bytes",
            "LOGIN_MAX_ATTEMPTS": 5,
            "LOGIN_ATTEMPT_WINDOW_SECONDS": 300,
            "MODO_DESARROLLO": True,
            "GOOGLE_CLIENT_ID": "",
            "GOOGLE_LOGIN_CLIENT_ID": "",
            "GOOGLE_CLIENT_SECRET": "",
            "GOOGLE_REFRESH_TOKEN": "",
            "GOOGLE_SENDER_EMAIL": "",
            "SES_ENABLED": False,
            "SES_REGION": "us-east-2",
            "SES_SENDER_EMAIL": "",
            "TURNSTILE_SECRET_KEY": "",
        }
    )
    with application.app_context():
        seed_database()
        yield application
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_headers(client):
    response = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "admin@psicoconecta.com", "password": "Admin123*"},
    )
    return {"Authorization": f"Bearer {response.json['access_token']}"}

