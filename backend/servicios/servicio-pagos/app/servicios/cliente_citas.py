import requests
from flask import current_app, request

from app.utilidades.errores import ErrorDominio


class ClienteCitas:
    @staticmethod
    def obtener_cita(cita_id):
        autorizacion = request.headers.get("Authorization", "")
        try:
            respuesta = requests.get(
                f"{current_app.config['CITAS_SERVICE_URL']}/api/citas/{cita_id}",
                headers={"Authorization": autorizacion},
                timeout=current_app.config["SERVICE_TIMEOUT"],
            )
        except requests.RequestException:
            raise ErrorDominio(
                "El servicio de citas no está disponible.",
                503,
                "servicio_citas_no_disponible",
            ) from None
        if respuesta.status_code == 404:
            raise ErrorDominio("La cita no existe.", 404, "cita_no_encontrada")
        if respuesta.status_code in {401, 403}:
            raise ErrorDominio("No tienes acceso a esta cita.", respuesta.status_code, "acceso_denegado")
        if respuesta.status_code != 200:
            raise ErrorDominio(
                "No fue posible consultar la cita.",
                503 if respuesta.status_code >= 500 else respuesta.status_code,
                "consulta_cita_fallida",
            )
        datos = respuesta.json()
        return datos.get("cita") if isinstance(datos, dict) and "cita" in datos else datos

    @staticmethod
    def listar_citas(estado=None):
        autorizacion = request.headers.get("Authorization", "")
        parametros = {"estado": estado} if estado else None
        try:
            respuesta = requests.get(
                f"{current_app.config['CITAS_SERVICE_URL']}/api/citas",
                headers={"Authorization": autorizacion},
                params=parametros,
                timeout=current_app.config["SERVICE_TIMEOUT"],
            )
        except requests.RequestException:
            raise ErrorDominio(
                "El servicio de citas no está disponible.",
                503,
                "servicio_citas_no_disponible",
            ) from None
        if respuesta.status_code in {401, 403}:
            raise ErrorDominio(
                "No tienes permisos para sincronizar las citas.",
                respuesta.status_code,
                "acceso_denegado",
            )
        if respuesta.status_code != 200:
            raise ErrorDominio(
                "No fue posible consultar las citas.",
                503 if respuesta.status_code >= 500 else respuesta.status_code,
                "consulta_citas_fallida",
            )
        datos = respuesta.json()
        return datos if isinstance(datos, list) else datos.get("citas", [])
