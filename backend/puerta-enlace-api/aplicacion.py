import os

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SERVICIOS = {
    "usuarios": os.getenv("USUARIOS_SERVICE_URL", "http://127.0.0.1:5001"),
    "citas": os.getenv("CITAS_SERVICE_URL", "http://127.0.0.1:5002"),
    "teleconsulta": os.getenv("TELECONSULTA_SERVICE_URL", "http://127.0.0.1:5003"),
    "pagos": os.getenv("PAGOS_SERVICE_URL", "http://127.0.0.1:5004"),
    "inteligencia_iot": os.getenv("IOT_SERVICE_URL", "http://127.0.0.1:5005"),
}


@app.get("/health")
def health():
    return jsonify(estado="ok", servicio="puerta-enlace-api")


import requests
from flask import request, Response

@app.route("/api/servicios")
def servicios():
    return jsonify(servicios=SERVICIOS)

def proxy_request(url, path=""):
    target_url = f"{url}/{path}" if path else url
    # Reenviar headers, omitiendo host
    headers = {k:v for k,v in request.headers if k.lower() != 'host'}
    
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        params=request.args
    )
    
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    return Response(resp.content, resp.status_code, headers)

@app.route("/api/citas", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/api/citas/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_citas(subpath=""):
    return proxy_request(f"{SERVICIOS['citas']}/api/citas", subpath)

@app.route("/api/disponibilidad", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/api/disponibilidad/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_disponibilidad(subpath=""):
    return proxy_request(f"{SERVICIOS['citas']}/api/disponibilidad", subpath)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
