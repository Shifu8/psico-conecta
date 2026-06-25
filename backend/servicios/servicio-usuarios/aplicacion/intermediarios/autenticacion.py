# Archivo: autenticacion.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

from flask_jwt_extended import get_jwt_identity

from aplicacion.extensiones import db
from aplicacion.modelos import User


def get_current_user():
    identity = get_jwt_identity()
    try:
        return db.session.get(User, int(identity)) if identity else None
    except (TypeError, ValueError):
        return None

