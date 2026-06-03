import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


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
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_LOGIN_CLIENT_ID = os.getenv("GOOGLE_LOGIN_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")
    GOOGLE_SENDER_EMAIL = os.getenv("GOOGLE_SENDER_EMAIL", "")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", FRONTEND_URL).split(",")
        if origin.strip()
    ]
