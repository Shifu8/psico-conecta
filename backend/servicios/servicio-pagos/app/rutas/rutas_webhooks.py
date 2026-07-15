from flask import Blueprint, jsonify, request

from app.servicios.servicio_pagos import ServicioPagos


bp_webhooks = Blueprint("webhooks_pagos", __name__)


@bp_webhooks.post("/stripe")
def webhook_stripe():
    resultado = ServicioPagos.procesar_webhook(
        request.get_data(cache=False),
        request.headers.get("Stripe-Signature", ""),
    )
    return jsonify(resultado)
