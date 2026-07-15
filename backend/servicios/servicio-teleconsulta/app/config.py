import json
import os


def _booleano(nombre, defecto=False):
    valor = os.getenv(nombre)
    if valor is None:
        return defecto
    return valor.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


def _origenes():
    return [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if x.strip()]


def _hosts_zoom():
    bruto = os.getenv("ZOOM_HOSTS_JSON", "{}").strip() or "{}"
    try:
        datos = json.loads(bruto)
    except json.JSONDecodeError:
        datos = {}
    return {str(clave): str(valor).strip() for clave, valor in datos.items() if str(valor).strip()}


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_TOKEN_LOCATION = ["headers"]

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///teleconsulta.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    DB_SCHEMA = os.getenv("DB_SCHEMA", os.getenv("DATABASE_SCHEMA", "teleconsulta_schema"))

    USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:5001").rstrip("/")
    CITAS_SERVICE_URL = os.getenv("CITAS_SERVICE_URL", "http://localhost:5002").rstrip("/")
    SERVICE_TIMEOUT = float(os.getenv("SERVICE_TIMEOUT", "4"))
    VALIDAR_USUARIO_REMOTO = _booleano("VALIDAR_USUARIO_REMOTO", False)
    INTERNAL_SERVICE_TOKEN = os.getenv("TELECONSULTA_INTERNAL_TOKEN", "")

    PAGOS_SERVICE_URL = os.getenv("PAGOS_SERVICE_URL", "http://localhost:5004").rstrip("/")
    PAGOS_INTERNAL_TOKEN = os.getenv("PAGOS_INTERNAL_TOKEN", "").strip()
    REQUIRE_PAYMENT_FOR_TELECONSULTA = _booleano("REQUIRE_PAYMENT_FOR_TELECONSULTA", False)

    ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID", "").strip()
    ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID", "").strip()
    ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET", "").strip()
    ZOOM_HOST_USER_ID = os.getenv("ZOOM_HOST_USER_ID", "").strip()
    ZOOM_HOSTS = _hosts_zoom()
    ZOOM_WEBHOOK_SECRET_TOKEN = os.getenv("ZOOM_WEBHOOK_SECRET_TOKEN", "").strip()
    ZOOM_API_BASE_URL = os.getenv("ZOOM_API_BASE_URL", "https://api.zoom.us/v2").rstrip("/")
    ZOOM_OAUTH_URL = os.getenv("ZOOM_OAUTH_URL", "https://zoom.us/oauth/token")
    ZOOM_TIMEOUT = float(os.getenv("ZOOM_TIMEOUT", "10"))

    TIMEZONE = os.getenv("TIMEZONE", "America/Guayaquil")
    ACCESO_ANTES_PACIENTE_MIN = int(os.getenv("ACCESO_ANTES_PACIENTE_MIN", "10"))
    ACCESO_ANTES_PSICOLOGO_MIN = int(os.getenv("ACCESO_ANTES_PSICOLOGO_MIN", "15"))
    ACCESO_DESPUES_FIN_MIN = int(os.getenv("ACCESO_DESPUES_FIN_MIN", "30"))
    CORS_ORIGINS = _origenes()
    JSON_SORT_KEYS = False
