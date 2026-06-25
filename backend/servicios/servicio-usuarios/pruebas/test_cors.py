# Archivo: test_cors.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

def test_api_agrega_cors_sin_origin(client):
    response = client.get("/api/usuarios/autenticacion/google/configuracion")

    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert "Authorization" in response.headers["Access-Control-Allow-Headers"]
    assert "Content-Type" in response.headers["Access-Control-Allow-Headers"]


def test_api_responde_preflight_cors(client):
    response = client.options(
        "/api/usuarios/autenticacion/registro",
        headers={
            "Origin": "https://psico-conecta.brandon-medina.workers.dev",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 204
    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert "Content-Type" in response.headers["Access-Control-Allow-Headers"]
    assert "POST" in response.headers["Access-Control-Allow-Methods"]
