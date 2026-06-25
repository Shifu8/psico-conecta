# Archivo: tiempo.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

from datetime import UTC, datetime


def utc_now():
    """Devuelve UTC sin zona para columnas SQL y evita utcnow() obsoleto."""
    return datetime.now(UTC).replace(tzinfo=None)
