from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def requiere_rol(*roles):
    """
    Decorador para proteger endpoints por rol.
    Verifica que el token JWT sea válido y que el rol del usuario 
    (incluido en los claims del token) coincida con alguno de los roles permitidos.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get("rol")
                
                if not user_role or user_role not in roles:
                    return jsonify({"error": "Acceso no autorizado", "mensaje": f"Se requiere uno de los siguientes roles: {', '.join(roles)}"}), 403
                    
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": "Error de autenticación", "mensaje": str(e)}), 401
        return decorator
    return wrapper
