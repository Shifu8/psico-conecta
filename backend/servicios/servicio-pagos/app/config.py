import os


def _booleano(nombre, defecto=False):
    valor = os.getenv(nombre)
    if valor is None:
        return defecto
    return valor.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


def _origenes():
    valor = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [item.strip() for item in valor.split(",") if item.strip()]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_TOKEN_LOCATION = ["headers"]

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///pagos.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    DB_SCHEMA = os.getenv("DB_SCHEMA", os.getenv("DATABASE_SCHEMA", "pagos_schema"))

    USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:5001").rstrip("/")
    CITAS_SERVICE_URL = os.getenv("CITAS_SERVICE_URL", "http://localhost:5002").rstrip("/")
    SERVICE_TIMEOUT = float(os.getenv("SERVICE_TIMEOUT", "5"))
    VALIDAR_USUARIO_REMOTO = _booleano("VALIDAR_USUARIO_REMOTO", False)

    INTERNAL_SERVICE_TOKEN = os.getenv("PAGOS_INTERNAL_TOKEN", "").strip()

    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip()
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
    STRIPE_MAX_NETWORK_RETRIES = int(os.getenv("STRIPE_MAX_NETWORK_RETRIES", "2"))

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    DEFAULT_CONSULTATION_PRICE_CENTS = int(os.getenv("DEFAULT_CONSULTATION_PRICE_CENTS", "3000"))
    DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD").strip().upper()
    CHECKOUT_EXPIRES_MINUTES = max(30, min(1440, int(os.getenv("CHECKOUT_EXPIRES_MINUTES", "30"))))
    AUTO_REFUND_ON_CANCEL = _booleano("AUTO_REFUND_ON_CANCEL", True)
    REQUIRE_PAYMENT_FOR_TELECONSULTA = _booleano("REQUIRE_PAYMENT_FOR_TELECONSULTA", False)

    CORS_ORIGINS = _origenes()
    JSON_SORT_KEYS = False
