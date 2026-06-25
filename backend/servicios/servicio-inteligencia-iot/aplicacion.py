# Archivo: aplicacion.py
# Descripción: Punto de entrada principal e inicialización del servidor.
# Módulo: Servicio IoT

import os

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
emociones = []
lecturas_iot = []


@app.get("/health")
def health():
    return jsonify(
        estado="ok",
        servicio="servicio-inteligencia-iot",
        almacenamiento="dynamodb",
        mensajeria="aws_iot_core",
    )


@app.route("/api/iot/emociones", methods=["GET", "POST"])
def coleccion_emociones():
    if request.method == "POST":
        entrada = {"id": len(emociones) + 1, **(request.get_json(silent=True) or {})}
        emociones.append(entrada)
        return jsonify(emocion=entrada), 201
    return jsonify(emociones=emociones)


@app.route("/api/iot/lecturas", methods=["GET", "POST"])
def coleccion_lecturas():
    if request.method == "POST":
        entrada = {"id": len(lecturas_iot) + 1, **(request.get_json(silent=True) or {})}
        lecturas_iot.append(entrada)
        return jsonify(lectura_iot=entrada), 201
    return jsonify(lecturas_iot=lecturas_iot)


@app.get("/api/iot/configuracion")
def configuracion_iot():
    return jsonify(
        proveedor="aws_iot_core",
        protocolo="mqtt",
        tiempo_real="websockets",
        tablas=["emociones", "lecturas_iot", "notificaciones", "logs_iot"],
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5005")))
