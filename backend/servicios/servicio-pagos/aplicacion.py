# Archivo: aplicacion.py
# Descripción: Punto de entrada principal e inicialización del servidor.
# Módulo: Servicio Pagos

import os

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
pagos = []


@app.get("/health")
def health():
    return jsonify(estado="ok", servicio="servicio-pagos", modo="stripe_sandbox")


@app.post("/api/pagos/crear-pago")
def crear_pago():
    pago = {
        "id": len(pagos) + 1,
        "estado": "simulado",
        "proveedor": "stripe_sandbox",
        **(request.get_json(silent=True) or {}),
    }
    pagos.append(pago)
    return jsonify(pago=pago), 201


@app.get("/api/pagos")
def listar_pagos():
    return jsonify(pagos=pagos)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5004")))
