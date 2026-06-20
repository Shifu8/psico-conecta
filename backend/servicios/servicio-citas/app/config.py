import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///citas.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    
    # Custom config for schema
    DB_SCHEMA = os.getenv("DB_SCHEMA", "citas_schema")
    USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:5001")
