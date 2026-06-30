# Archivo: autenticacion.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from aplicacion.extensiones import db
from aplicacion.intermediarios.autenticacion import get_current_user
from aplicacion.modelos import TokenBlocklist
from aplicacion.esquemas.autenticacion import (
    ForgotPasswordSchema,
    GoogleLoginSchema,
    LoginSchema,
    RegisterSchema,
    ResetPasswordSchema,
)
from aplicacion.servicios.servicio_autenticacion import (
    InvalidCredentialsError,
    authenticate_user,
    create_password_reset,
    register_user,
    reset_password,
)
from aplicacion.servicios.servicio_auditoria import registrar_evento_auditoria
from aplicacion.servicios.servicio_captcha import verificar_captcha
from aplicacion.servicios.servicio_cognito import register_user_cognito
from aplicacion.servicios.servicio_google_login import google_login as google_login_service
from aplicacion.servicios.servicio_gmail import enviar_correo_recuperacion
from aplicacion.utilidades.intentos_login import (
    TooManyLoginAttemptsError,
    clear_login_attempts,
    ensure_login_allowed,
    register_failed_login,
)

auth_bp = Blueprint("autenticacion", __name__, url_prefix="/api/usuarios/autenticacion")


@auth_bp.post("/registro")
def register():
    data = RegisterSchema().load(request.get_json(silent=True) or {})
    verificar_captcha(data.get("captcha_token"), request.remote_addr)
    cognito_response = None
    if current_app.config["COGNITO_ENABLED"]:
        cognito_response = register_user_cognito(
            data["email"],
            data["password"],
            data["first_name"],
            data["last_name"],
        )
    user = register_user(data)
    if cognito_response:
        user.cognito_sub = cognito_response.get("UserSub")
        db.session.commit()
    registrar_evento_auditoria(
        "register_success",
        "autenticacion",
        target=user,
        request_obj=request,
        detail={"metodo": "formulario"},
    )
    return jsonify(message="Usuario registrado correctamente.", user=user.to_dict()), 201


@auth_bp.post("/inicio-sesion")
def login():
    data = LoginSchema().load(request.get_json(silent=True) or {})
    verificar_captcha(data.get("captcha_token"), request.remote_addr)
    ip_address = request.remote_addr
    try:
        ensure_login_allowed(ip_address, data["email"])
    except TooManyLoginAttemptsError as error:
        registrar_evento_auditoria(
            "login_blocked",
            "autenticacion",
            status="failure",
            actor_email=data["email"].strip().lower(),
            request_obj=request,
            detail={"motivo": "demasiados_intentos", "espera_segundos": error.retry_after},
            descripcion="Acceso bloqueado temporalmente por 24 horas. El usuario superó el límite de 3 intentos fallidos."
        )
        raise
    try:
        user, access_token = authenticate_user(data)
    except InvalidCredentialsError:
        register_failed_login(ip_address, data["email"])
        from flask import current_app
        from aplicacion.utilidades.intentos_login import _key, _config, _LOCK
        max_attempts, window = _config()
        key = _key(ip_address, data["email"])
        with _LOCK:
            attempts = list(current_app.extensions.get("login_attempts", {}).get(key, []))
        num_intento = len(attempts)
        desc = f"Intento fallido de inicio de sesión #{num_intento} de {max_attempts}."
        if num_intento >= max_attempts:
            desc += " Límite alcanzado, cuenta bloqueada temporalmente por 24 horas."
            
        registrar_evento_auditoria(
            "login_failed",
            "autenticacion",
            status="failure",
            actor_email=data["email"].strip().lower(),
            request_obj=request,
            detail={"motivo": "credenciales_invalidas", "intento": num_intento, "max_intentos": max_attempts},
            descripcion=desc
        )
        raise
    except ValueError as error:
        registrar_evento_auditoria(
            "login_failed",
            "autenticacion",
            status="failure",
            actor_email=data["email"].strip().lower(),
            request_obj=request,
            detail={"motivo": str(error)},
        )
        raise
    clear_login_attempts(ip_address, data["email"])
    registrar_evento_auditoria(
        "login_success",
        "autenticacion",
        actor=user,
        request_obj=request,
        detail={"metodo": "correo"},
    )
    return jsonify(access_token=access_token, user=user.to_dict())


@auth_bp.post("/cierre-sesion")
@jwt_required()
def logout():
    user = get_current_user()
    db.session.add(TokenBlocklist(jti=get_jwt()["jti"]))
    db.session.commit()
    registrar_evento_auditoria(
        "logout",
        "autenticacion",
        actor=user,
        request_obj=request,
    )
    return jsonify(message="Sesion cerrada correctamente.")


@auth_bp.post("/recuperar-contrasena")
def forgot_password():
    data = ForgotPasswordSchema().load(request.get_json(silent=True) or {})
    verificar_captcha(data.get("captcha_token"), request.remote_addr)
    token = create_password_reset(data["email"])
    registrar_evento_auditoria(
        "password_reset_requested",
        "autenticacion",
        actor_email=data["email"].strip().lower(),
        request_obj=request,
        detail={"token_generado": bool(token)},
    )
    response = {"message": "Si el correo está registrado, recibirás instrucciones por correo."}
    if token:
        resultado = enviar_correo_recuperacion(data["email"], token)
        response["correo_enviado"] = resultado["enviado"]
    if token and current_app.config["MODO_DESARROLLO"] and not response["correo_enviado"]:
        response["reset_token"] = token
    return jsonify(response)


@auth_bp.post("/restablecer-contrasena")
def reset_password_route():
    data = ResetPasswordSchema().load(request.get_json(silent=True) or {})
    reset_password(data["token"], data["password"])
    return jsonify(message="Contraseña actualizada correctamente.")


@auth_bp.get("/mi-perfil")
@jwt_required()
def me():
    user = get_current_user()
    if not user or user.status != "active":
        return jsonify(message="Usuario inactivo o inexistente."), 403
    return jsonify(user=user.to_dict())


@auth_bp.post("/google")
def google_auth():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict) or not payload.get("credential"):
        return jsonify(message="Token de Google requerido."), 400
    data = GoogleLoginSchema().load(payload)
    try:
        user, access_token, creado = google_login_service(data["credential"])
        registrar_evento_auditoria(
            "google_register_success" if creado else "google_login_success",
            "autenticacion",
            actor=user,
            target=user if creado else None,
            request_obj=request,
            detail={"metodo": "google"},
        )
        return jsonify(access_token=access_token, user=user.to_dict())
    except ValueError as e:
        registrar_evento_auditoria(
            "google_login_failed",
            "autenticacion",
            status="failure",
            request_obj=request,
            detail={"motivo": str(e)},
        )
        return jsonify(message=str(e)), 400


@auth_bp.get("/google/configuracion")
def google_login_configuration():
    cid = (
        current_app.config.get("GOOGLE_LOGIN_CLIENT_ID")
        or current_app.config.get("GOOGLE_CLIENT_ID", "")
    )
    if cid:
        return jsonify({
            "habilitado": True,
            "client_id": cid,
        })
    return jsonify({
        "habilitado": False,
        "mensaje": "Configura GOOGLE_LOGIN_CLIENT_ID en el archivo .env.",
    })


