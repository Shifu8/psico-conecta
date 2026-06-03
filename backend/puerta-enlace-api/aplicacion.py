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


@app.get("/api/servicios")
def servicios():
    return jsonify(servicios=SERVICIOS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
