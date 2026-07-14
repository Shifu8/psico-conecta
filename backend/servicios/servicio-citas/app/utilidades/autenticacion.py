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


def _normalizar_rol(valor):
    return _MAPA_ROLES.get(str(valor or "").upper(), str(valor or "").upper())


def _extraer_rol(claims):
    return _normalizar_rol(claims.get("rol") or claims.get("role"))


def _extraer_id_usuario():
    identidad = get_jwt_identity()
    try:
        usuario_id = int(identidad)
    except (TypeError, ValueError):
        raise ErrorDominio(
            "La identidad contenida en el token no es válida.",
            401,
            "token_invalido",
        ) from None
    if usuario_id <= 0:
        raise ErrorDominio(
            "La identidad contenida en el token no es válida.",
            401,
            "token_invalido",
        )
    return usuario_id


def _consultar_perfil_remoto(usuario_id):
    if not current_app.config.get("VALIDAR_USUARIO_REMOTO", False):
        return None

    autorizacion = request.headers.get("Authorization")
    if not autorizacion:
        raise ErrorDominio("Se requiere autenticación.", 401, "autenticacion_requerida")

    url = (
        f"{current_app.config['USERS_SERVICE_URL']}"
        "/api/usuarios/autenticacion/mi-perfil"
    )
    try:
        respuesta = requests.get(
            url,
            headers={"Authorization": autorizacion},
            timeout=current_app.config["USERS_SERVICE_TIMEOUT"],
        )
    except requests.RequestException as error:
        current_app.logger.warning("No se pudo validar el usuario: %s", error)
        raise ErrorDominio(
            "El servicio de usuarios no está disponible para validar la sesión.",
            503,
            "servicio_usuarios_no_disponible",
        ) from None

    if respuesta.status_code in {401, 422}:
        raise ErrorDominio(
            "La sesión no es válida o fue cerrada.", 401, "token_invalido"
        )
    if respuesta.status_code == 403:
        raise ErrorDominio(
            "El usuario está inactivo o no tiene acceso.", 403, "usuario_inactivo"
        )
    if respuesta.status_code != 200:
        raise ErrorDominio(
            "No fue posible validar la sesión con el servicio de usuarios.",
            503,
            "validacion_usuario_fallida",
        )

    perfil = respuesta.json().get("user") or {}
    if int(perfil.get("id", -1)) != usuario_id:
        raise ErrorDominio(
            "La identidad de la sesión no coincide con el usuario.",
            401,
            "token_invalido",
        )
    if perfil.get("status") != "active":
        raise ErrorDominio(
            "El usuario está inactivo.", 403, "usuario_inactivo"
        )
    return perfil


def validar_psicologo_activo(psicologo_id):
    """Verifica contra usuarios que el ID corresponda a un psicólogo activo."""
    if not current_app.config.get("VALIDAR_USUARIO_REMOTO", False):
        return

    autorizacion = request.headers.get("Authorization")
    url = f"{current_app.config['USERS_SERVICE_URL']}/api/usuarios/psicologos"
    try:
        respuesta = requests.get(
            url,
            headers={"Authorization": autorizacion},
            timeout=current_app.config["USERS_SERVICE_TIMEOUT"],
        )
    except requests.RequestException as error:
        current_app.logger.warning("No se pudo consultar psicólogos: %s", error)
        raise ErrorDominio(
            "El servicio de usuarios no está disponible.",
            503,
            "servicio_usuarios_no_disponible",
        ) from None

    if respuesta.status_code != 200:
        raise ErrorDominio(
            "No fue posible verificar al profesional seleccionado.",
            503 if respuesta.status_code >= 500 else respuesta.status_code,
            "validacion_psicologo_fallida",
        )

    psicologos = respuesta.json().get("psicologos") or []
    existe = any(int(usuario.get("id", -1)) == int(psicologo_id) for usuario in psicologos)
    if not existe:
        raise ErrorDominio(
            "El profesional seleccionado no existe o no está activo.",
            400,
            "psicologo_no_disponible",
        )


def requiere_rol(*roles_permitidos):
    roles_permitidos = {_normalizar_rol(rol) for rol in roles_permitidos}

    def envoltorio(funcion):
        @wraps(funcion)
        def decorador(*args, **kwargs):
            verify_jwt_in_request()
            usuario_id = _extraer_id_usuario()
            rol = _extraer_rol(get_jwt())
            perfil = _consultar_perfil_remoto(usuario_id)
            if perfil:
                rol = _normalizar_rol(perfil.get("role"))

            if not rol or rol not in roles_permitidos:
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
