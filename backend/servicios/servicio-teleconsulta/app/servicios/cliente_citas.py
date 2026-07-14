import requests
from flask import current_app, request

from app.utilidades.errores import ErrorDominio


class ClienteCitas:
    @staticmethod
    def _headers():
        autorizacion = request.headers.get("Authorization")
        return {"Authorization": autorizacion} if autorizacion else {}

    @staticmethod
    def _obtener(ruta):
        try:
            respuesta = requests.get(
                f"{current_app.config['CITAS_SERVICE_URL']}{ruta}",
                headers=ClienteCitas._headers(),
                timeout=current_app.config["SERVICE_TIMEOUT"],
            )
        except requests.RequestException:
            raise ErrorDominio(
                "El servicio de citas no está disponible.",
                503,
                "servicio_citas_no_disponible",
            ) from None
        if respuesta.status_code != 200:
            datos = respuesta.json() if respuesta.headers.get("content-type", "").startswith("application/json") else {}
            raise ErrorDominio(
                datos.get("mensaje") or datos.get("message") or "No fue posible consultar la cita.",
                respuesta.status_code,
                datos.get("error", "consulta_cita_fallida"),
            )
        return respuesta.json()

    @staticmethod
    def obtener_cita(cita_id):
        return ClienteCitas._obtener(f"/api/citas/{cita_id}")

    @staticmethod
    def mis_citas():
        datos = ClienteCitas._obtener("/api/citas/mis-citas")
        return datos if isinstance(datos, list) else []
