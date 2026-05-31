import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from servicio_zoom import crear_reunion_zoom

app = Flask(__name__)
CORS(app)
sesiones = []


@app.get("/health")
def health():
    return jsonify(estado="ok", servicio="servicio-teleconsulta")


@app.post("/api/teleconsulta/zoom/crear-reunion")
def crear_reunion():
    reunion = crear_reunion_zoom(request.get_json(silent=True) or {})
    sesiones.append(reunion)
    return jsonify(reunion=reunion), 201


@app.get("/api/teleconsulta/sesiones")
def listar_sesiones():
    return jsonify(sesiones=sesiones)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5003")))


