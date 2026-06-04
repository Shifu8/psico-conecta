def test_api_agrega_cors_sin_origin(client):
    response = client.options("/api/usuarios/autenticacion/registro")

    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert "Authorization" in response.headers["Access-Control-Allow-Headers"]
    assert "Content-Type" in response.headers["Access-Control-Allow-Headers"]
