from functools import wraps

from flask import jsonify
from flask_jwt_extended import jwt_required

from aplicacion.intermediarios.autenticacion import get_current_user


def role_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        @jwt_required()
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if not user or user.status != "active":
                return jsonify(message="Usuario inactivo o inexistente."), 403
            if user.role.name not in allowed_roles:
                return jsonify(message="No tienes permisos para esta accion."), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator


