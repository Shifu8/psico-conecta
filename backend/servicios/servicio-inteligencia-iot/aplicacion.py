# Archivo: aplicacion.py
# Descripción: Punto de entrada principal e inicialización del servidor híbrido (Flask API + WebSocket Server).
# Módulo: Servicio IoT

import os
import sys
import asyncio
from http import HTTPStatus
from flask import Flask, jsonify, request
from flask_cors import CORS
import websockets

# Asegurar importación del módulo de telemetría
sys.path.append(os.path.dirname(__file__))
from telemetria.aplicacion import handler as ws_telemetria_handler, loop_limpieza_buffer

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


def handle_flask_request(path, method, headers_dict, body):
    with app.test_client() as client:
        res = client.open(path, method=method, headers=headers_dict, data=body)
        resp_headers = [(k, v) for k, v in res.headers.items()]
        return (HTTPStatus(res.status_code), resp_headers, res.data)


async def process_request(path, request_headers):
    # Si la petición incluye Upgrade: websocket, cedemos el control al handler de websockets
    upgrade = request_headers.get("Upgrade", "").lower()
    if upgrade == "websocket":
        return None
    
    # De lo contrario, procesamos la petición HTTP REST con Flask
    headers_dict = dict(request_headers)
    method = request_headers.get("Method", "GET")
    return handle_flask_request(path, method, headers_dict, b"")


async def main():
    port = int(os.getenv("PORT", "5005"))
    print(f"[+] Iniciando servidor unificado de IoT (Flask API + WebSocket) en el puerto {port}...")
    
    # Iniciar persistencia asíncrona de fondo
    asyncio.create_task(loop_limpieza_buffer())
    
    # Servidor híbrido en el puerto único expuesto por Docker/AWS
    async with websockets.serve(ws_telemetria_handler, "0.0.0.0", port, process_request=process_request):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[-] Servidor unificado IoT detenido.")
