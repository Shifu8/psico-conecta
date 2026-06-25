# Archivo: servicio_gmail.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

import base64
from email.message import EmailMessage
from urllib.parse import urlencode

from flask import current_app


ASUNTO_RECUPERACION = "Recupera tu acceso a PsicoConecta"


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


def configuracion_ses_completa():
    return bool(
        current_app.config.get("SES_ENABLED")
        and str(current_app.config.get("SES_SENDER_EMAIL", "")).strip()
    )


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


def _detalle_error(error):
    detalle = str(error).strip() or type(error).__name__
    return detalle[:300]


def _crear_contenido_recuperacion(enlace):
    texto = (
        "Recibimos una solicitud para actualizar tu contrasena.\n\n"
        f"Abre este enlace temporal: {enlace}\n\n"
        "El enlace expira en 30 minutos. Si no solicitaste el cambio, ignoralo."
    )
    html = (
        "<p>Recibimos una solicitud para actualizar tu contrasena.</p>"
        f'<p><a href="{enlace}">Restablecer contrasena</a></p>'
        "<p>El enlace expira en 30 minutos. "
        "Si no solicitaste el cambio, ignoralo.</p>"
    )
    return texto, html


def _enviar_con_gmail(destinatario, enlace):
    texto, _html = _crear_contenido_recuperacion(enlace)
    mensaje = EmailMessage()
    mensaje["To"] = destinatario
    mensaje["From"] = current_app.config["GOOGLE_SENDER_EMAIL"]
    mensaje["Subject"] = ASUNTO_RECUPERACION
    mensaje.set_content(texto)
    contenido = base64.urlsafe_b64encode(mensaje.as_bytes()).decode("utf-8")
    respuesta = (
        _crear_cliente_gmail()
        .users()
        .messages()
        .send(userId="me", body={"raw": contenido})
        .execute()
    )
    return {"enviado": True, "modo": "gmail_api", "id_mensaje": respuesta.get("id")}


def _enviar_con_ses(destinatario, enlace):
    import boto3

    texto, html = _crear_contenido_recuperacion(enlace)
    cliente = boto3.client("sesv2", region_name=current_app.config["SES_REGION"])
    respuesta = cliente.send_email(
        FromEmailAddress=current_app.config["SES_SENDER_EMAIL"],
        Destination={"ToAddresses": [destinatario]},
        Content={
            "Simple": {
                "Subject": {"Data": ASUNTO_RECUPERACION, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": texto, "Charset": "UTF-8"},
                    "Html": {"Data": html, "Charset": "UTF-8"},
                },
            }
        },
    )
    return {"enviado": True, "modo": "ses", "id_mensaje": respuesta.get("MessageId")}


def enviar_correo_recuperacion(destinatario, token):
    """Envia el enlace por Gmail API, con respaldo SES si esta configurado."""
    parametros = urlencode({"token": token})
    enlace = f"{current_app.config['FRONTEND_URL']}/restablecer-contrasena?{parametros}"

    if configuracion_gmail_completa():
        try:
            return _enviar_con_gmail(destinatario, enlace)
        except Exception as error:
            current_app.logger.warning(
                "No se pudo enviar correo de recuperacion con Gmail API: %s: %s",
                type(error).__name__,
                _detalle_error(error),
            )
    else:
        current_app.logger.info("Gmail API no configurada. Se usara otro proveedor si existe.")

    if configuracion_ses_completa():
        try:
            return _enviar_con_ses(destinatario, enlace)
        except Exception as error:
            current_app.logger.warning(
                "No se pudo enviar correo de recuperacion con SES: %s: %s",
                type(error).__name__,
                _detalle_error(error),
            )

    return {"enviado": False, "modo": "sin_proveedor", "enlace": enlace}
