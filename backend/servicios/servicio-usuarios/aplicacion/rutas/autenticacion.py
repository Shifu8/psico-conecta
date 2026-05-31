from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from aplicacion.extensiones import db
from aplicacion.intermediarios.autenticacion import get_current_user
from aplicacion.modelos import TokenBlocklist
from aplicacion.esquemas.autenticacion import (
    ForgotPasswordSchema,
    LoginSchema,
    RegisterSchema,
    ResetPasswordSchema,
)
from aplicacion.servicios.servicio_autenticacion import (
    authenticate_user,
    create_password_reset,
    register_user,
    reset_password,
)
from aplicacion.servicios.servicio_cognito import register_user_cognito
from aplicacion.servicios.servicio_google_login import google_login as google_login_service
from aplicacion.servicios.servicio_gmail import enviar_correo_recuperacion

auth_bp = Blueprint("autenticacion", __name__, url_prefix="/api/usuarios/autenticacion")


@auth_bp.post("/registro")
def register():
    data = RegisterSchema().load(request.get_json(silent=True) or {})
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
    return jsonify(message="Usuario registrado correctamente.", user=user.to_dict()), 201


@auth_bp.post("/inicio-sesion")
def login():
    data = LoginSchema().load(request.get_json(silent=True) or {})
    user, access_token = authenticate_user(data)
    return jsonify(access_token=access_token, user=user.to_dict())


@auth_bp.post("/cierre-sesion")
@jwt_required()
def logout():
    db.session.add(TokenBlocklist(jti=get_jwt()["jti"]))
    db.session.commit()
    return jsonify(message="Sesion cerrada correctamente.")


@auth_bp.post("/recuperar-contrasena")
def forgot_password():
    data = ForgotPasswordSchema().load(request.get_json(silent=True) or {})
    token = create_password_reset(data["email"])
    response = {"message": "Si el correo existe, recibiras instrucciones por correo."}
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
    return jsonify(message="Contrasena actualizada correctamente.")


@auth_bp.get("/mi-perfil")
@jwt_required()
def me():
    user = get_current_user()
    if not user or user.status != "active":
        return jsonify(message="Usuario inactivo o inexistente."), 403
    return jsonify(user=user.to_dict())


@auth_bp.post("/google")
def google_auth():
    data = request.get_json(silent=True) or {}
    credential = data.get("credential")
    if not credential:
        return jsonify(message="Token de Google requerido."), 400
    try:
        user, access_token = google_login_service(credential)
        return jsonify(access_token=access_token, user=user.to_dict())
    except ValueError as e:
        return jsonify(message=str(e)), 400


@auth_bp.get("/google/configuracion")
def google_login_configuration():
    cid = current_app.config.get(
        "GOOGLE_LOGIN_CLIENT_ID",
        current_app.config.get("GOOGLE_CLIENT_ID", ""),
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


