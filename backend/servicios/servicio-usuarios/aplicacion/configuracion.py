import os
from datetime import timedelta
from pathlib import Path

from dotenv import dotenv_values, load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent


def encontrar_repo_dir():
    for ruta in (BASE_DIR, *BASE_DIR.parents):
        if (ruta / "frontend").exists() and (ruta / "backend").exists():
            return ruta
    return BASE_DIR


REPO_DIR = encontrar_repo_dir()
ENV_FILES = (
    BASE_DIR / ".env",
    REPO_DIR / ".env",
    REPO_DIR / "frontend" / ".env.development.local",
    REPO_DIR / "frontend" / ".env.development",
    REPO_DIR / "frontend" / ".env.local",
    REPO_DIR / "frontend" / ".env",
)
GOOGLE_LOGIN_CLIENT_ID_PRODUCCION = (
    "339658076678-kah0e205d5asf6ufnlh009lh5i4g8u70.apps.googleusercontent.com"
)
load_dotenv(BASE_DIR / ".env")


DOTENV_VALUES = {
    env_file: dotenv_values(env_file)
    for env_file in ENV_FILES
    if env_file.exists()
}


def env_value(*names, default=""):
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    for name in names:
        for values in DOTENV_VALUES.values():
            value = values.get(name)
            if value and value.strip():
                return value.strip()
    return default


class Config:
    MODO_DESARROLLO = os.getenv("MODO_DESARROLLO", "true").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "local-dev-secret-change-me-now-please")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
    )
    LOGIN_MAX_ATTEMPTS = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
    LOGIN_ATTEMPT_WINDOW_SECONDS = int(
        os.getenv("LOGIN_ATTEMPT_WINDOW_SECONDS", "300")
    )
    _database_url = os.getenv("DATABASE_URL", "")
    if _database_url.startswith("postgresql://") and "+psycopg" not in _database_url:
        _database_url = _database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    SQLALCHEMY_DATABASE_URI = _database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "usuarios_schema")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    COGNITO_ENABLED = os.getenv("COGNITO_ENABLED", "false").lower() == "true"
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "")
    COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "")
    COGNITO_CLIENT_SECRET = os.getenv("COGNITO_CLIENT_SECRET", "")
    COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN", "")
    COGNITO_GOOGLE_REDIRECT_URI = os.getenv(
        "COGNITO_GOOGLE_REDIRECT_URI", "http://localhost:5173/iniciar-sesion"
    )
    GOOGLE_CLIENT_ID = env_value("GOOGLE_CLIENT_ID")
    GOOGLE_LOGIN_CLIENT_ID = env_value("GOOGLE_LOGIN_CLIENT_ID", "VITE_GOOGLE_CLIENT_ID")
    if not GOOGLE_LOGIN_CLIENT_ID and not MODO_DESARROLLO:
        GOOGLE_LOGIN_CLIENT_ID = GOOGLE_LOGIN_CLIENT_ID_PRODUCCION
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")
    GOOGLE_SENDER_EMAIL = os.getenv("GOOGLE_SENDER_EMAIL", "")
    SES_ENABLED = os.getenv("SES_ENABLED", "false").lower() == "true"
    SES_REGION = os.getenv("SES_REGION", AWS_REGION)
    SES_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL", GOOGLE_SENDER_EMAIL)
    CAPTCHA_DESACTIVADO = os.getenv("CAPTCHA_DESACTIVADO", "false").lower() == "true"
    TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", FRONTEND_URL).split(",")
        if origin.strip()
    ]
