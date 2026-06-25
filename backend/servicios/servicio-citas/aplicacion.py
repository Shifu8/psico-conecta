# Archivo: aplicacion.py
# Descripción: Punto de entrada principal e inicialización del servidor.
# Módulo: Servicio Citas

import os

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
citas = []


@app.get("/health")
def health():
    return jsonify(estado="ok", servicio="servicio-citas")


@app.get("/api/citas")
def listar_citas():
    return jsonify(citas=citas)


@app.post("/api/citas")
def crear_cita():
    cita = {"id": len(citas) + 1, **(request.get_json(silent=True) or {})}
    citas.append(cita)
    return jsonify(cita=cita), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5002")))
