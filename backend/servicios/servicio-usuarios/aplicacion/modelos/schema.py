# Archivo: schema.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

import os


def obtener_schema():
    database_url = os.environ.get("DATABASE_URL", "").lower()
    if database_url.startswith("sqlite"):
        return None
    return os.environ.get("DATABASE_SCHEMA", "usuarios_schema") or None


def prefijo_schema(schema):
    return f"{schema}." if schema else ""
