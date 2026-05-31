def test_listar_roles(client, admin_headers):
    response = client.get("/api/usuarios/roles", headers=admin_headers)
    assert response.status_code == 200
    assert "roles" in response.json
    names = [r["name"] for r in response.json["roles"]]
    assert "ADMIN" in names
    assert "PSYCHOLOGIST" in names
    assert "PATIENT" in names


def test_crear_rol(client, admin_headers):
    response = client.post(
        "/api/usuarios/roles",
        json={"name": "recepcionista", "description": "Rol de prueba", "permissions": []},
        headers=admin_headers,
    )
    assert response.status_code == 201
    assert response.json["role"]["name"] == "RECEPCIONISTA"


def test_crear_rol_duplicado(client, admin_headers):
    response = client.post(
        "/api/usuarios/roles",
        json={"name": "recepcionista", "description": "Rol de prueba", "permissions": []},
        headers=admin_headers,
    )
    assert response.status_code == 201
    response = client.post(
        "/api/usuarios/roles",
        json={"name": "recepcionista", "description": "Rol dup", "permissions": []},
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "existe" in response.json["message"]


def test_actualizar_rol(client, admin_headers):
    roles = client.get("/api/usuarios/roles", headers=admin_headers)
    role_id = roles.json["roles"][0]["id"]
    response = client.put(
        f"/api/usuarios/roles/{role_id}",
        json={"name": "soporte", "description": "Actualizado", "permissions": []},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json["role"]["name"] == "SOPORTE"


def test_no_admin_no_puede_gestionar_roles(client):
    login = client.post(
        "/api/usuarios/autenticacion/inicio-sesion",
        json={"email": "paciente@psicoconecta.com", "password": "Paciente123*"},
    )
    headers = {"Authorization": f"Bearer {login.json['access_token']}"}
    response = client.get("/api/usuarios/roles", headers=headers)
    assert response.status_code == 403
