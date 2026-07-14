import os


def _booleano(nombre, defecto=False):
    valor = os.getenv(nombre)
    if valor is None:
        return defecto
    return valor.strip().lower() in {"1", "true", "si", "sí", "yes", "on"}


def _origenes():
    valor = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [origen.strip() for origen in valor.split(",") if origen.strip()]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///citas.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_TOKEN_LOCATION = ["headers"]

    DB_SCHEMA = os.getenv("DB_SCHEMA", "citas_schema")
    USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:5001").rstrip("/")
    USERS_SERVICE_TIMEOUT = float(os.getenv("USERS_SERVICE_TIMEOUT", "3"))
    VALIDAR_USUARIO_REMOTO = _booleano("VALIDAR_USUARIO_REMOTO", False)

    TELECONSULTA_SERVICE_URL = os.getenv("TELECONSULTA_SERVICE_URL", "http://localhost:5003").rstrip("/")
    TELECONSULTA_INTERNAL_TOKEN = os.getenv("TELECONSULTA_INTERNAL_TOKEN", "")
    TELECONSULTA_TIMEOUT = float(os.getenv("TELECONSULTA_TIMEOUT", "5"))

    TIMEZONE = os.getenv("TIMEZONE", "America/Guayaquil")
    CORS_ORIGINS = _origenes()
    JSON_SORT_KEYS = False
