import logging
import os
import time

import requests
from flask import Flask, Response, jsonify, request
from flask_cors import CORS


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("puerta-enlace-api")

app = Flask(__name__)


def _origenes():
    valor = os.getenv("CORS_ORIGINS", "*")
    if valor.strip() == "*":
        return "*"
    return [origen.strip() for origen in valor.split(",") if origen.strip()]


CORS(
    app,
    resources={r"/api/*": {"origins": _origenes()}},
    allow_headers=["Authorization", "Content-Type", "Stripe-Signature", "X-Internal-Token"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)

SERVICIOS = {
    "usuarios": os.getenv("USUARIOS_SERVICE_URL", "http://127.0.0.1:5001").rstrip("/"),
    "citas": os.getenv("CITAS_SERVICE_URL", "http://127.0.0.1:5002").rstrip("/"),
    "teleconsulta": os.getenv("TELECONSULTA_SERVICE_URL", "http://127.0.0.1:5003").rstrip("/"),
    "pagos": os.getenv("PAGOS_SERVICE_URL", "http://127.0.0.1:5004").rstrip("/"),
    "inteligencia_iot": os.getenv("IOT_SERVICE_URL", "http://127.0.0.1:5005").rstrip("/"),
}

PROXY_TIMEOUT_CONNECT = float(os.getenv("PROXY_TIMEOUT_CONNECT", "3"))
PROXY_TIMEOUT_READ = float(os.getenv("PROXY_TIMEOUT_READ", "30"))


@app.before_request
def registrar_entrada():
    request.inicio_proxy = time.monotonic()
    logger.info(
        "[AUDITORÍA] Acceso entrante - IP: %s - Método: %s - Ruta: %s - Auth: %s",
        request.remote_addr,
        request.method,
        request.path,
        "presente" if request.headers.get("Authorization") else "ausente",
    )


@app.after_request
def registrar_salida(respuesta):
    duracion = time.monotonic() - getattr(request, "inicio_proxy", time.monotonic())
    logger.info(
        "[AUDITORÍA] Respuesta enviada - IP: %s - Ruta: %s - Código: %s - Duración: %.4fs",
        request.remote_addr,
        request.path,
        respuesta.status_code,
        duracion,
    )
    return respuesta


@app.get("/health")
def health():
    return jsonify(estado="ok", servicio="puerta-enlace-api")


def proxy_request(url_base, subpath=""):
    destino = f"{url_base}/{subpath.lstrip('/')}" if subpath else url_base
    headers = {
        clave: valor
        for clave, valor in request.headers
        if clave.lower() not in {"host", "content-length", "connection"}
    }
    headers["X-Forwarded-For"] = request.headers.get(
        "X-Forwarded-For", request.remote_addr or ""
    )
    headers["X-Forwarded-Proto"] = request.headers.get("X-Forwarded-Proto", request.scheme)
    headers["X-Forwarded-Host"] = request.headers.get("Host", "")

    try:
        respuesta = requests.request(
            method=request.method,
            url=destino,
            headers=headers,
            data=request.get_data(cache=False),
            cookies=request.cookies,
            allow_redirects=False,
            params=request.args,
            timeout=(PROXY_TIMEOUT_CONNECT, PROXY_TIMEOUT_READ),
        )
    except requests.Timeout:
        return jsonify(
            error="servicio_no_disponible",
            mensaje="El servicio tardó demasiado en responder.",
        ), 504
    except requests.RequestException as error:
        logger.warning("No se pudo acceder a %s: %s", destino, error)
        return jsonify(
            error="servicio_no_disponible",
            mensaje="El servicio solicitado no está disponible temporalmente.",
        ), 503

    excluidas = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    headers_salida = [
        (nombre, valor)
        for nombre, valor in respuesta.raw.headers.items()
        if nombre.lower() not in excluidas
    ]
    return Response(respuesta.content, respuesta.status_code, headers_salida)


@app.route("/api/usuarios", defaults={"subpath": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/usuarios/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_usuarios(subpath):
    return proxy_request(f"{SERVICIOS['usuarios']}/api/usuarios", subpath)


@app.route("/api/citas", defaults={"subpath": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/citas/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_citas(subpath):
    return proxy_request(f"{SERVICIOS['citas']}/api/citas", subpath)


@app.route("/api/disponibilidad", defaults={"subpath": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/disponibilidad/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_disponibilidad(subpath):
    return proxy_request(f"{SERVICIOS['citas']}/api/disponibilidad", subpath)


@app.route("/api/teleconsultas", defaults={"subpath": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/teleconsultas/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_teleconsultas(subpath):
    return proxy_request(f"{SERVICIOS['teleconsulta']}/api/teleconsultas", subpath)


@app.route("/api/pagos", defaults={"subpath": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/pagos/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_pagos(subpath):
    return proxy_request(f"{SERVICIOS['pagos']}/api/pagos", subpath)


@app.route("/api/iot", defaults={"subpath": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/iot/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_iot(subpath):
    return proxy_request(f"{SERVICIOS['inteligencia_iot']}/api/iot", subpath)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
