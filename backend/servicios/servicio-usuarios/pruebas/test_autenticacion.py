def test_register_exitoso(client):
    response = client.post(
        "/api/usuarios/autenticacion/registro",
        json={
            "first_name": "Ana",
            "last_name": "Perez",
            "email": "ana@example.com",
            "password": "Segura123*",
        },
    )
    assert response.status_code == 201
    assert response.json["user"]["role"] == "PATIENT"
    assert response.json["user"]["email"] == "ana@example.com"
    assert "password_hash" not in response.json["user"]


def test_register_duplicado(client):
    client.post(
        "/api/usuarios/autenticacion/registro",
        json={"first_name": "Ana", "last_name": "Perez", "email": "ana@example.com", "password": "Segura123*"},
    )
    response = client.post(
        "/api/usuarios/autenticacion/registro",
        json={"first_name": "Ana", "last_name": "Perez", "email": "ana@example.com", "password": "OtraClave456*"},
    )
    assert response.status_code == 400
    assert "existe" in response.json["message"]


def test_register_campos_faltantes(client):
    response = client.post(
        "/api/usuarios/autenticacion/registro",
        json={"email": "solo@correo.com"},
    )
    assert response.status_code == 400


def test_register_email_invalido(client):
    response = client.post(
        "/api/usuarios/autenticacion/registro",
        json={"first_name": "Ana", "last_name": "Perez", "email": "no-es-email", "password": "Segura123*"},
    )
    assert response.status_code == 400


def test_register_password_corta(client):
    response = client.post(
        "/api/usuarios/autenticacion/registro",
        json={"first_name": "Ana", "last_name": "Perez", "email": "ana@example.com", "password": "123"},
    )
    assert response.status_code == 400


def test_login_exitoso(client):
    client.post(
        "/api/usuarios/autenticacion/registro",
        json={"first_name": "Luis", "last_name": "Rojas", "email": "luis@example.com", "password": "ClaveSegura99*"},
    )
    response = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "luis@example.com", "password": "ClaveSegura99*"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json
    assert response.json["user"]["email"] == "luis@example.com"


def test_login_credenciales_incorrectas(client):
    response = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "noexiste@example.com", "password": "Clave123*"},
    )
    assert response.status_code == 400
    assert "incorrectos" in response.json["message"]


def test_login_contrasena_incorrecta(client):
    client.post(
        "/api/usuarios/autenticacion/registro",
        json={"first_name": "Luis", "last_name": "Rojas", "email": "luis@example.com", "password": "ClaveSegura99*"},
    )
    response = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "luis@example.com", "password": "OtraClave123*"},
    )
    assert response.status_code == 400


def test_login_usuario_inactivo(client):
    login = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "admin@psicoconecta.com", "password": "Admin123*"},
    )
    headers = {"Authorization": f"Bearer {login.json['access_token']}"}
    client.patch(
        "/api/usuarios/1/status",
        json={"status": "inactive"},
        headers=headers,
    )
    response = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "admin@psicoconecta.com", "password": "Admin123*"},
    )
    assert response.status_code == 400
    assert "inactiva" in response.json["message"]


def test_logout_y_token_revocado(client):
    client.post(
        "/api/usuarios/autenticacion/registro",
        json={"first_name": "Luis", "last_name": "Rojas", "email": "luis@example.com", "password": "ClaveSegura99*"},
    )
    login = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "luis@example.com", "password": "ClaveSegura99*"},
    )
    headers = {"Authorization": f"Bearer {login.json['access_token']}"}
    assert client.get("/api/usuarios/autenticacion/mi-perfil", headers=headers).status_code == 200
    assert client.post("/api/usuarios/autenticacion/cierre-sesion", headers=headers).status_code == 200
    assert client.get("/api/usuarios/autenticacion/mi-perfil", headers=headers).status_code == 401


def test_mi_perfil_sin_token(client):
    response = client.get("/api/usuarios/autenticacion/mi-perfil")
    assert response.status_code == 401


def test_mi_perfil_token_invalido(client):
    response = client.get(
        "/api/usuarios/autenticacion/mi-perfil",
        headers={"Authorization": "Bearer token-falso"},
    )
    assert response.status_code == 422


def test_recuperacion_local(client):
    response = client.post(
        "/api/usuarios/autenticacion/recuperar-contrasena",
        json={"email": "paciente@psicoconecta.com"},
    )
    assert response.status_code == 200
    token = response.json.get("reset_token")
    assert token is not None

    reset = client.post(
        "/api/usuarios/autenticacion/restablecer-contrasena",
        json={"token": token, "password": "NuevaClave123*"},
    )
    assert reset.status_code == 200

    login = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "paciente@psicoconecta.com", "password": "NuevaClave123*"},
    )
    assert login.status_code == 200


def test_recuperacion_email_inexistente(client):
    response = client.post(
        "/api/usuarios/autenticacion/recuperar-contrasena",
        json={"email": "noexiste@example.com"},
    )
    assert response.status_code == 200
    assert response.json.get("reset_token") is None


def test_recuperacion_token_invalido(client):
    response = client.post(
        "/api/usuarios/autenticacion/restablecer-contrasena",
        json={"token": "token-falso", "password": "NuevaClave123*"},
    )
    assert response.status_code == 400
    assert "token" in response.json["message"]


def test_google_configuracion(client):
    response = client.get("/api/usuarios/autenticacion/google/configuracion")
    assert response.status_code == 200
    assert "habilitado" in response.json
    assert response.json["habilitado"] is False


def test_google_configuracion_usa_client_id_compatible(client, app):
    app.config["GOOGLE_CLIENT_ID"] = "web-client-id.apps.googleusercontent.com"
    response = client.get("/api/usuarios/autenticacion/google/configuracion")
    assert response.status_code == 200
    assert response.json["habilitado"] is True
    assert response.json["client_id"] == "web-client-id.apps.googleusercontent.com"


def test_google_login_sin_token(client):
    response = client.post("/api/usuarios/autenticacion/google", json={})
    assert response.status_code == 400
    assert "Token" in response.json["message"]


def test_google_login_sin_configuracion(client):
    response = client.post(
        "/api/usuarios/autenticacion/google",
        json={"credential": "token-falso"},
    )
    assert response.status_code == 400
    assert "configurado" in response.json["message"]


def test_google_login_token_invalido(client, app, monkeypatch):
    app.config["GOOGLE_LOGIN_CLIENT_ID"] = "web-client-id.apps.googleusercontent.com"

    def rechazar_token(*_args, **_kwargs):
        raise ValueError

    monkeypatch.setattr(
        "aplicacion.servicios.servicio_google_login.id_token.verify_oauth2_token",
        rechazar_token,
    )
    response = client.post(
        "/api/usuarios/autenticacion/google",
        json={"credential": "token-falso"},
    )
    assert response.status_code == 400
    assert "token" in response.json["message"]
