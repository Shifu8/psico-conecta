# Archivo: servicio_cognito.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

from urllib.parse import urlencode

from flask import current_app


def _client():
    if not current_app.config["COGNITO_ENABLED"]:
        return None
    import boto3

    return boto3.client("cognito-idp", region_name=current_app.config["AWS_REGION"])


def register_user_cognito(email, password, first_name, last_name):
    client = _client()
    if not client:
        return None
    return client.sign_up(
        ClientId=current_app.config["COGNITO_CLIENT_ID"],
        Username=email,
        Password=password,
        UserAttributes=[
            {"Name": "email", "Value": email},
            {"Name": "given_name", "Value": first_name},
            {"Name": "family_name", "Value": last_name},
        ],
    )


def login_user_cognito(email, password):
    client = _client()
    if not client:
        return None
    return client.initiate_auth(
        ClientId=current_app.config["COGNITO_CLIENT_ID"],
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": email, "PASSWORD": password},
    )


def obtener_configuracion_login_google():
    """Prepara Google -> Cognito sin implementar OAuth directo en Flask."""
    requeridas = ("COGNITO_DOMAIN", "COGNITO_CLIENT_ID")
    if not current_app.config["COGNITO_ENABLED"] or not all(
        current_app.config[variable] for variable in requeridas
    ):
        return {
            "habilitado": False,
            "mensaje": "Configura Cognito Hosted UI y el proveedor Google.",
        }
    parametros = urlencode(
        {
            "client_id": current_app.config["COGNITO_CLIENT_ID"],
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": current_app.config["COGNITO_GOOGLE_REDIRECT_URI"],
            "identity_provider": "Google",
        }
    )
    return {
        "habilitado": True,
        "url_autorizacion": f"{current_app.config['COGNITO_DOMAIN']}/oauth2/authorize?{parametros}",
    }
