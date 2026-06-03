import base64
from email.message import EmailMessage
from urllib.parse import urlencode

from flask import current_app


def configuracion_gmail_completa():
    variables = (
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REFRESH_TOKEN",
        "GOOGLE_SENDER_EMAIL",
    )
    faltantes = [
        variable
        for variable in variables
        if not str(current_app.config.get(variable, "")).strip()
    ]
    if faltantes:
        current_app.logger.warning(
            "Gmail API no configurada. Faltan variables: %s",
            ", ".join(faltantes),
        )
    return not faltantes


def _crear_cliente_gmail():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    credenciales = Credentials(
        token=None,
        refresh_token=current_app.config["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=current_app.config["GOOGLE_CLIENT_ID"],
        client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/gmail.send"],
    )
    if not credenciales.valid and credenciales.refresh_token:
        credenciales.refresh(Request())
    return build("gmail", "v1", credentials=credenciales, cache_discovery=False)


def enviar_correo_recuperacion(destinatario, token):
    """Envia el enlace por Gmail API o informa modo local sin usar SMTP."""
    parametros = urlencode({"token": token})
    enlace = f"{current_app.config['FRONTEND_URL']}/restablecer-contrasena?{parametros}"
    if not configuracion_gmail_completa():
        current_app.logger.info("Gmail API no configurada. Se usará el modo local.")
        return {"enviado": False, "modo": "local", "enlace": enlace}

    mensaje = EmailMessage()
    mensaje["To"] = destinatario
    mensaje["From"] = current_app.config["GOOGLE_SENDER_EMAIL"]
    mensaje["Subject"] = "Recupera tu acceso a PsicoConecta"
    mensaje.set_content(
        "Recibimos una solicitud para actualizar tu contrasena.\n\n"
        f"Abre este enlace temporal: {enlace}\n\n"
        "El enlace expira en 30 minutos. Si no solicitaste el cambio, ignoralo."
    )
    contenido = base64.urlsafe_b64encode(mensaje.as_bytes()).decode("utf-8")
    try:
        respuesta = (
            _crear_cliente_gmail()
            .users()
            .messages()
            .send(userId="me", body={"raw": contenido})
            .execute()
        )
    except Exception as error:
        current_app.logger.warning(
            "No se pudo enviar correo de recuperacion con Gmail API: %s",
            type(error).__name__,
        )
        return {"enviado": False, "modo": "gmail_api", "error": type(error).__name__}
    return {"enviado": True, "modo": "gmail_api", "id_mensaje": respuesta.get("id")}
