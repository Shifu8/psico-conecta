import requests
from flask import current_app

from app.utilidades.errores import ErrorDominio


class ClientePagos:
    @staticmethod
    def estado_cita(cita_id):
        url = current_app.config.get("PAGOS_SERVICE_URL")
        token = current_app.config.get("PAGOS_INTERNAL_TOKEN")
        if not url or not token:
            raise ErrorDominio(
                "El servicio de pagos no está configurado.",
                503,
                "servicio_pagos_no_configurado",
            )
        try:
            respuesta = requests.get(
                f"{url}/api/pagos/interna/citas/{cita_id}/estado",
                headers={"X-Internal-Token": token},
                timeout=current_app.config.get("SERVICE_TIMEOUT", 5),
            )
        except requests.RequestException:
            raise ErrorDominio(
                "No fue posible verificar el pago de la cita.",
                503,
                "servicio_pagos_no_disponible",
            ) from None
        if respuesta.status_code != 200:
            raise ErrorDominio(
                "No fue posible verificar el pago de la cita.",
                503 if respuesta.status_code >= 500 else respuesta.status_code,
                "validacion_pago_fallida",
            )
        return respuesta.json()
