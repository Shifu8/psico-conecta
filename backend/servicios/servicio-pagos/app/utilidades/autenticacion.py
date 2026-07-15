from functools import wraps

import requests
from flask import current_app, g, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app.utilidades.errores import ErrorDominio


_MAPA_ROLES = {
    "PATIENT": "PACIENTE",
    "PACIENTE": "PACIENTE",
    "PSYCHOLOGIST": "PSICOLOGO",
    "PSICOLOGO": "PSICOLOGO",
    "PSICÓLOGO": "PSICOLOGO",
    "ADMIN": "ADMIN",
    "ADMINISTRADOR": "ADMIN",
}


def normalizar_rol(valor):
    return _MAPA_ROLES.get(str(valor or "").upper(), str(valor or "").upper())


def _usuario_id():
    try:
        usuario_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        raise ErrorDominio("La identidad de la sesión no es válida.", 401, "token_invalido") from None
    if usuario_id <= 0:
        raise ErrorDominio("La identidad de la sesión no es válida.", 401, "token_invalido")
    return usuario_id


def _validar_perfil(usuario_id):
    if not current_app.config["VALIDAR_USUARIO_REMOTO"]:
        return None
    autorizacion = request.headers.get("Authorization")
    if not autorizacion:
        raise ErrorDominio("Se requiere autenticación.", 401, "autenticacion_requerida")
    try:
        respuesta = requests.get(
            f"{current_app.config['USERS_SERVICE_URL']}/api/usuarios/autenticacion/mi-perfil",
            headers={"Authorization": autorizacion},
            timeout=current_app.config["SERVICE_TIMEOUT"],
        )
    except requests.RequestException:
        raise ErrorDominio(
            "El servicio de usuarios no está disponible para validar la sesión.",
            503,
            "servicio_usuarios_no_disponible",
        ) from None
    if respuesta.status_code in {401, 422}:
        raise ErrorDominio("La sesión no es válida o fue cerrada.", 401, "token_invalido")
    if respuesta.status_code == 403:
        raise ErrorDominio("El usuario está inactivo.", 403, "usuario_inactivo")
    if respuesta.status_code != 200:
        raise ErrorDominio("No fue posible validar la sesión.", 503, "validacion_usuario_fallida")
    perfil = respuesta.json().get("user") or {}
    if int(perfil.get("id", -1)) != usuario_id or perfil.get("status") != "active":
        raise ErrorDominio("La sesión no corresponde a un usuario activo.", 401, "token_invalido")
    return perfil


def requiere_rol(*roles):
    permitidos = {normalizar_rol(rol) for rol in roles}

    def envoltorio(funcion):
        @wraps(funcion)
        def decorador(*args, **kwargs):
            verify_jwt_in_request()
            usuario_id = _usuario_id()
            claims = get_jwt()
            rol = normalizar_rol(claims.get("rol") or claims.get("role"))
            perfil = _validar_perfil(usuario_id)
            if perfil:
                rol = normalizar_rol(perfil.get("role"))
            if rol not in permitidos:
                return jsonify(
                    error="acceso_denegado",
                    mensaje="No tienes permisos para realizar esta operación.",
                ), 403
            g.usuario_id = usuario_id
            g.usuario_rol = rol
            g.usuario_perfil = perfil
            return funcion(*args, **kwargs)

        return decorador

    return envoltorio


def requiere_token_interno(funcion):
    @wraps(funcion)
    def decorador(*args, **kwargs):
        esperado = current_app.config["INTERNAL_SERVICE_TOKEN"]
        recibido = request.headers.get("X-Internal-Token", "")
        if not esperado or recibido != esperado:
            raise ErrorDominio("Credencial interna inválida.", 401, "token_interno_invalido")
        return funcion(*args, **kwargs)

    return decorador
