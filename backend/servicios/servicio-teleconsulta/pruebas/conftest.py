import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Las pruebas usan SQLite y no deben crear schemas de PostgreSQL.
os.environ.pop("DB_SCHEMA", None)
os.environ.pop("DATABASE_SCHEMA", None)

from flask_jwt_extended import create_access_token

from app import create_app, db


class ZoomFalso:
    def __init__(self):
        self.reuniones = {}
        self.eliminadas = []
        self.contador = 90000000000

    def configurado(self):
        return True

    def resolver_host(self, psicologo_id):
        return f"psicologo-{psicologo_id}@example.com"

    def crear_reunion(self, host_user_id, payload):
        self.contador += 1
        meeting_id = str(self.contador)
        reunion = {
            "id": meeting_id,
            "uuid": f"uuid-{meeting_id}",
            "join_url": f"https://zoom.example/j/{meeting_id}?pwd=segura",
            "start_url": f"https://zoom.example/s/{meeting_id}?zak=temporal",
            "password": "segura",
            "host": host_user_id,
            "payload": payload,
        }
        self.reuniones[meeting_id] = reunion
        return reunion.copy()

    def actualizar_reunion(self, meeting_id, payload):
        self.reuniones[str(meeting_id)]["payload"] = payload
        return {}

    def obtener_reunion(self, meeting_id):
        return self.reuniones[str(meeting_id)].copy()

    def eliminar_reunion(self, meeting_id):
        meeting_id = str(meeting_id)
        self.eliminadas.append(meeting_id)
        self.reuniones.pop(meeting_id, None)
        return {}


@pytest.fixture()
def app(tmp_path):
    archivo = tmp_path / "teleconsulta_test.db"
    app = create_app(
        test_config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{archivo}",
            "JWT_SECRET_KEY": "test-secret-key-with-more-than-32-characters",
            "VALIDAR_USUARIO_REMOTO": False,
            "CORS_ORIGINS": ["http://localhost:5173"],
            "INTERNAL_SERVICE_TOKEN": "internal-test-token",
            "ZOOM_ACCOUNT_ID": "account-test",
            "ZOOM_CLIENT_ID": "client-test",
            "ZOOM_CLIENT_SECRET": "secret-test",
            "ZOOM_HOST_USER_ID": "host@example.com",
            "ZOOM_HOSTS": {},
            "TIMEZONE": "America/Guayaquil",
            "ACCESO_ANTES_PACIENTE_MIN": 10,
            "ACCESO_ANTES_PSICOLOGO_MIN": 15,
            "ACCESO_DESPUES_FIN_MIN": 30,
        }
    )
    zoom = ZoomFalso()
    app.extensions["zoom_client"] = zoom
    app.zoom_falso = zoom
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def cliente(app):
    return app.test_client()


@pytest.fixture()
def token(app):
    def crear(usuario_id, rol):
        with app.app_context():
            return create_access_token(identity=str(usuario_id), additional_claims={"role": rol})
    return crear


@pytest.fixture()
def cita_virtual_confirmada():
    inicio = datetime.now(timezone.utc) + timedelta(minutes=5)
    return {
        "id": "a735d0a6-01ab-4ca2-9be4-5d9c0ff4b7b0",
        "paciente_id": 20,
        "psicologo_id": 10,
        "fecha_hora_inicio": inicio.isoformat(),
        "fecha_hora_fin": (inicio + timedelta(minutes=50)).isoformat(),
        "estado": "CONFIRMADA",
        "modalidad": "VIRTUAL",
    }
