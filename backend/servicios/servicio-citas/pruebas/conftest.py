import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

# Las pruebas usan SQLite; no deben intentar crear el schema de PostgreSQL.
os.environ.pop("DB_SCHEMA", None)
from flask_jwt_extended import create_access_token

from app import create_app, db
from app.modelos.disponibilidad import Disponibilidad


@pytest.fixture()
def app(tmp_path):
    archivo = tmp_path / "citas_test.db"
    app = create_app(
        test_config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{archivo}",
            "JWT_SECRET_KEY": "test-secret-key-with-more-than-32-characters",
            "VALIDAR_USUARIO_REMOTO": False,
            "CORS_ORIGINS": ["http://localhost:5173"],
            "TIMEZONE": "America/Guayaquil",
        }
    )
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
            return create_access_token(
                identity=str(usuario_id), additional_claims={"role": rol}
            )
    return crear


@pytest.fixture()
def fecha_habil_futura():
    zona = ZoneInfo("America/Guayaquil")
    fecha = datetime.now(zona).date() + timedelta(days=2)
    while fecha.weekday() > 4:
        fecha += timedelta(days=1)
    return fecha


@pytest.fixture()
def disponibilidad(app, fecha_habil_futura):
    with app.app_context():
        bloque = Disponibilidad(
            psicologo_id=10,
            dia_semana=fecha_habil_futura.weekday(),
            hora_inicio=datetime.strptime("08:00", "%H:%M").time(),
            hora_fin=datetime.strptime("12:00", "%H:%M").time(),
            duracion_slot=50,
        )
        db.session.add(bloque)
        db.session.commit()
        return str(bloque.id)
