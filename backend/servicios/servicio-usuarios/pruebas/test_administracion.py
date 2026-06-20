from io import BytesIO

def test_admin_lista_usuarios(client, admin_headers):
    response = client.get("/api/usuarios", headers=admin_headers)
    assert response.status_code == 200
    assert "users" in response.json
    assert len(response.json["users"]) >= 3


def test_admin_obtener_usuario_por_id(client, admin_headers):
    users = client.get("/api/usuarios", headers=admin_headers)
    user_id = users.json["users"][0]["id"]
    response = client.get(f"/api/usuarios/{user_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json["user"]["id"] == user_id


def test_admin_editar_usuario(client, admin_headers):
    users = client.get("/api/usuarios", headers=admin_headers)
    user_id = users.json["users"][-1]["id"]
    response = client.put(
        f"/api/usuarios/{user_id}",
        json={"first_name": "NombreEditado"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json["user"]["first_name"] == "NombreEditado"


def test_admin_desactivar_usuario(client, admin_headers):
    users = client.get("/api/usuarios", headers=admin_headers)
    patient = next(u for u in users.json["users"] if u["role"] == "PATIENT")
    response = client.patch(
        f"/api/usuarios/{patient['id']}/status",
        json={"status": "inactive"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json["user"]["status"] == "inactive"


def test_admin_reactivar_usuario(client, admin_headers):
    users = client.get("/api/usuarios", headers=admin_headers)
    patient = next(u for u in users.json["users"] if u["role"] == "PATIENT")
    client.patch(
        f"/api/usuarios/{patient['id']}/status",
        json={"status": "inactive"},
        headers=admin_headers,
    )
    response = client.patch(
        f"/api/usuarios/{patient['id']}/status",
        json={"status": "active"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json["user"]["status"] == "active"


def test_no_admin_no_puede_listar_usuarios(client):
    login = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "paciente@psicoconecta.com", "password": "Paciente123*"},
    )
    headers = {"Authorization": f"Bearer {login.json['access_token']}"}
    response = client.get("/api/usuarios", headers=headers)
    assert response.status_code == 403


def test_paciente_puede_ver_su_perfil(client):
    login = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "paciente@psicoconecta.com", "password": "Paciente123*"},
    )
    headers = {"Authorization": f"Bearer {login.json['access_token']}"}
    response = client.get("/api/usuarios/autenticacion/mi-perfil", headers=headers)
    assert response.status_code == 200


def test_admin_panel(client, admin_headers):
    response = client.get("/api/usuarios/administrador/panel", headers=admin_headers)
    assert response.status_code == 200
    assert response.json["role"] == "ADMIN"


def test_paciente_no_puede_abrir_panel_admin(client):
    login = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "paciente@psicoconecta.com", "password": "Paciente123*"},
    )
    headers = {"Authorization": f"Bearer {login.json['access_token']}"}
    assert client.get("/api/usuarios/administrador/panel", headers=headers).status_code == 403
    assert client.get("/api/usuarios/paciente/panel", headers=headers).status_code == 200


def test_psicologo_panel(client):
    login = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "psicologo@psicoconecta.com", "password": "Psicologo123*"},
    )
    headers = {"Authorization": f"Bearer {login.json['access_token']}"}
    response = client.get("/api/usuarios/psicologo/panel", headers=headers)
    assert response.status_code == 200
    assert response.json["role"] == "PSYCHOLOGIST"


def test_usuario_puede_subir_foto_perfil(client):
    login = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "paciente@psicoconecta.com", "password": "Paciente123*"},
    )
    user_id = login.json["user"]["id"]
    headers = {"Authorization": f"Bearer {login.json['access_token']}"}
    png_minimo = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

    response = client.post(
        f"/api/usuarios/{user_id}/foto-perfil",
        data={"foto": (BytesIO(png_minimo), "perfil.png")},
        headers=headers,
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.json["user"]["profile_photo_url"].startswith(
        f"/api/usuarios/{user_id}/foto-perfil"
    )
    foto = client.get(f"/api/usuarios/{user_id}/foto-perfil")
    assert foto.status_code == 200
    assert foto.content_type.startswith("image/png")