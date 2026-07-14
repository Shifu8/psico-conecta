import hashlib
import hmac
import json
import time

from flask import Blueprint, current_app, jsonify, request

from app import db
from app.modelos import SesionZoom
from app.servicios.servicio_teleconsulta import ServicioTeleconsulta
from app.utilidades.errores import ErrorDominio
from app.utilidades.tiempo import ahora_utc

bp_webhooks = Blueprint("webhooks_zoom", __name__)


def _firma_valida(cuerpo):
    secreto = current_app.config["ZOOM_WEBHOOK_SECRET_TOKEN"]
    if not secreto:
        return False
    marca = request.headers.get("x-zm-request-timestamp", "")
    firma = request.headers.get("x-zm-signature", "")
    try:
        if abs(int(time.time()) - int(marca)) > 300:
            return False
    except ValueError:
        return False
    mensaje = f"v0:{marca}:".encode() + cuerpo
    calculada = "v0=" + hmac.new(secreto.encode(), mensaje, hashlib.sha256).hexdigest()
    return hmac.compare_digest(calculada, firma)


@bp_webhooks.post("/zoom")
def webhook_zoom():
    cuerpo = request.get_data(cache=True)
    try:
        evento = json.loads(cuerpo or b"{}")
    except json.JSONDecodeError:
        raise ErrorDominio("Webhook inválido.", 400, "webhook_invalido") from None

    if evento.get("event") == "endpoint.url_validation":
        secreto = current_app.config["ZOOM_WEBHOOK_SECRET_TOKEN"]
        token = (evento.get("payload") or {}).get("plainToken")
        if not secreto or not token:
            raise ErrorDominio("No se pudo validar el endpoint.", 400, "webhook_no_configurado")
        cifrado = hmac.new(secreto.encode(), token.encode(), hashlib.sha256).hexdigest()
        return jsonify(plainToken=token, encryptedToken=cifrado)

    if not _firma_valida(cuerpo):
        raise ErrorDominio("La firma del webhook no es válida.", 401, "firma_webhook_invalida")

    nombre = evento.get("event")
    objeto = ((evento.get("payload") or {}).get("object") or {})
    meeting_id = objeto.get("id")
    if not meeting_id:
        return jsonify(recibido=True)
    sesion = SesionZoom.query.filter_by(zoom_meeting_id=str(meeting_id)).first()
    if not sesion:
        return jsonify(recibido=True)

    if nombre == "meeting.started":
        sesion.estado = "EN_CURSO"
    elif nombre == "meeting.ended":
        sesion.estado = "FINALIZADA"
    elif nombre in {"meeting.deleted", "meeting.permanently_deleted"}:
        sesion.estado = "CANCELADA"
        sesion.enlace_acceso = None
    else:
        return jsonify(recibido=True)

    sesion.zoom_meeting_uuid = objeto.get("uuid") or sesion.zoom_meeting_uuid
    sesion.actualizado_en = ahora_utc()
    ServicioTeleconsulta._registrar(sesion, nombre.upper().replace(".", "_"), data={"zoom": objeto})
    db.session.commit()
    return jsonify(recibido=True)
