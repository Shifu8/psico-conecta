from datetime import timedelta

import pytest
from flask_jwt_extended import create_access_token


REGISTER_URL = "/api/usuarios/autenticacion/registro"
LOGIN_URL = "/api/usuarios/autenticacion/inicio-sesion"


def _register_payload(**changes):
    payload = {
        "first_name": "Ana",
        "last_name": "Perez",
        "email": "ana@example.com",
        "password": "Segura123*",
    }
    payload.update(changes)
    return payload


@pytest.mark.parametrize(
    "password",
    [
        "sinsimbolo1A",
        "SINMINUSCULA1*",
        "sinmayuscula1*",
        "SinNumero*",
        "Admin123*",
        "Con Espacio1*",
    ],
)
def test_registro_rechaza_password_debil(client, password):
    response = client.post(REGISTER_URL, json=_register_payload(password=password))
    assert response.status_code == 400
    assert "password" in response.json["errors"]


def test_registro_normaliza_datos_y_valida_telefono(client):
    response = client.post(
        REGISTER_URL,
        json=_register_payload(
            first_name="  Ana   Maria ",
            last_name=" Perez  ",
            email=" ANA@EXAMPLE.COM ",
            phone=" +593 99 123 4567 ",
        ),
    )
    assert response.status_code == 201
    assert response.json["user"]["first_name"] == "Ana Maria"
    assert response.json["user"]["last_name"] == "Perez"
    assert response.json["user"]["email"] == "ana@example.com"
    assert response.json["user"]["phone"] == "+593 99 123 4567"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("first_name", "Ana<script>"),
        ("last_name", "Perez123"),
        ("phone", "telefono-falso"),
    ],
)
def test_registro_rechaza_datos_personales_invalidos(client, field, value):
    response = client.post(REGISTER_URL, json=_register_payload(**{field: value}))
    assert response.status_code == 400
    assert field in response.json["errors"]


def test_registro_publico_no_permite_asignar_admin(client):
    response = client.post(REGISTER_URL, json=_register_payload(role="ADMIN"))
    assert response.status_code == 400
    assert "role" in response.json["errors"]


def test_respuesta_usuario_no_expone_identificadores_externos(client):
    response = client.post(REGISTER_URL, json=_register_payload())
    assert response.status_code == 201
    assert "password_hash" not in response.json["user"]
    assert "google_id" not in response.json["user"]
    assert "cognito_sub" not in response.json["user"]


def test_login_limita_intentos_fallidos(client):
    for _attempt in range(5):
        response = client.post(
            LOGIN_URL,
            json={"email": "bloqueado@example.com", "password": "Incorrecta123*"},
        )
        assert response.status_code == 400

    response = client.post(
        LOGIN_URL,
        json={"email": "bloqueado@example.com", "password": "Incorrecta123*"},
    )
    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_jwt_expirado_devuelve_mensaje_controlado(client, app):
    with app.app_context():
        token = create_access_token(
            identity="1",
            expires_delta=timedelta(seconds=-1),
        )
    response = client.get(
        "/api/usuarios/autenticacion/mi-perfil",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert "expiró" in response.json["message"]
    assert "detail" not in response.json


def test_jwt_con_identidad_no_numerica_no_genera_error_interno(client, app):
    with app.app_context():
        token = create_access_token(identity="identidad-invalida")
    response = client.get(
        "/api/usuarios/autenticacion/mi-perfil",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_restablecer_rechaza_password_debil(client):
    response = client.post(
        "/api/usuarios/autenticacion/restablecer-contrasena",
        json={"token": "token-falso", "password": "debil"},
    )
    assert response.status_code == 400
    assert "password" in response.json["errors"]


def test_google_login_exitoso_no_expone_identificadores(client, app, monkeypatch):
    app.config["GOOGLE_LOGIN_CLIENT_ID"] = "web-client-id.apps.googleusercontent.com"
    monkeypatch.setattr(
        "aplicacion.servicios.servicio_google_login.id_token.verify_oauth2_token",
        lambda *_args, **_kwargs: {
            "iss": "https://accounts.google.com",
            "email": "google@example.com",
            "email_verified": True,
            "sub": "google-sub-id",
            "given_name": "Ana",
            "family_name": "Google",
        },
    )
    response = client.post(
        "/api/usuarios/autenticacion/google",
        json={"credential": "token-google"},
    )
    assert response.status_code == 200
    assert response.json["user"]["role"] == "PATIENT"
    assert "google_id" not in response.json["user"]


def test_google_login_rechaza_correo_no_verificado(client, app, monkeypatch):
    app.config["GOOGLE_LOGIN_CLIENT_ID"] = "web-client-id.apps.googleusercontent.com"
    monkeypatch.setattr(
        "aplicacion.servicios.servicio_google_login.id_token.verify_oauth2_token",
        lambda *_args, **_kwargs: {
            "iss": "https://accounts.google.com",
            "email": "google@example.com",
            "email_verified": False,
            "sub": "google-sub-id",
        },
    )
    response = client.post(
        "/api/usuarios/autenticacion/google",
        json={"credential": "token-google"},
    )
    assert response.status_code == 400
    assert "correo" in response.json["message"]


def test_admin_editar_usuario_normaliza_datos(client, admin_headers):
    users = client.get("/api/usuarios", headers=admin_headers)
    user_id = users.json["users"][-1]["id"]
    response = client.put(
        f"/api/usuarios/{user_id}",
        json={"first_name": "  Ana   Maria ", "phone": " +593 99 123 4567 "},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json["user"]["first_name"] == "Ana Maria"
    assert response.json["user"]["phone"] == "+593 99 123 4567"


def test_admin_editar_usuario_rechaza_telefono_invalido(client, admin_headers):
    users = client.get("/api/usuarios", headers=admin_headers)
    user_id = users.json["users"][-1]["id"]
    response = client.put(
        f"/api/usuarios/{user_id}",
        json={"phone": "telefono-falso"},
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "phone" in response.json["errors"]


def test_admin_editar_usuario_rechaza_payload_vacio(client, admin_headers):
    users = client.get("/api/usuarios", headers=admin_headers)
    user_id = users.json["users"][-1]["id"]
    response = client.put(
        f"/api/usuarios/{user_id}",
        json={},
        headers=admin_headers,
    )
    assert response.status_code == 400
