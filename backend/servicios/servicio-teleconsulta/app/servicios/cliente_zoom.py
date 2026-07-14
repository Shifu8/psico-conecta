import threading
import time
from urllib.parse import quote

import requests
from flask import current_app

from app.utilidades.errores import ErrorDominio


class ClienteZoom:
    def __init__(self):
        self._token = None
        self._expira = 0
        self._bloqueo = threading.Lock()

    def configurado(self):
        cfg = current_app.config
        return all([cfg["ZOOM_ACCOUNT_ID"], cfg["ZOOM_CLIENT_ID"], cfg["ZOOM_CLIENT_SECRET"]])

    def resolver_host(self, psicologo_id):
        cfg = current_app.config
        return cfg["ZOOM_HOSTS"].get(str(psicologo_id)) or cfg["ZOOM_HOST_USER_ID"]

    def _token_acceso(self):
        if not self.configurado():
            raise ErrorDominio(
                "Zoom todavía no está configurado en el servidor.",
                503,
                "zoom_no_configurado",
            )
        with self._bloqueo:
            if self._token and time.time() < self._expira:
                return self._token
            cfg = current_app.config
            try:
                respuesta = requests.post(
                    cfg["ZOOM_OAUTH_URL"],
                    params={"grant_type": "account_credentials", "account_id": cfg["ZOOM_ACCOUNT_ID"]},
                    auth=(cfg["ZOOM_CLIENT_ID"], cfg["ZOOM_CLIENT_SECRET"]),
                    timeout=cfg["ZOOM_TIMEOUT"],
                )
            except requests.RequestException:
                raise ErrorDominio("No fue posible autenticar con Zoom.", 503, "zoom_no_disponible") from None
            if respuesta.status_code != 200:
                raise ErrorDominio(
                    self._mensaje_error(respuesta, "Zoom rechazó las credenciales OAuth."),
                    502,
                    "zoom_autenticacion_fallida",
                )
            datos = respuesta.json()
            self._token = datos.get("access_token")
            if not self._token:
                raise ErrorDominio(
                    "Zoom no devolvió un token de acceso.",
                    502,
                    "zoom_autenticacion_fallida",
                )
            self._expira = time.time() + max(int(datos.get("expires_in", 3600)) - 60, 60)
            return self._token

    @staticmethod
    def _mensaje_error(respuesta, defecto):
        try:
            datos = respuesta.json()
        except ValueError:
            return defecto
        return datos.get("message") or datos.get("reason") or datos.get("error_description") or defecto

    def _solicitud(self, metodo, ruta, codigos_aceptados=None, **kwargs):
        token = self._token_acceso()
        try:
            respuesta = requests.request(
                metodo,
                f"{current_app.config['ZOOM_API_BASE_URL']}{ruta}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                timeout=current_app.config["ZOOM_TIMEOUT"],
                **kwargs,
            )
        except requests.RequestException:
            raise ErrorDominio("Zoom no respondió a tiempo.", 503, "zoom_no_disponible") from None
        aceptados = set(codigos_aceptados or {200, 201, 204})
        if respuesta.status_code not in aceptados:
            raise ErrorDominio(
                self._mensaje_error(respuesta, "Zoom rechazó la operación."),
                502,
                "zoom_operacion_fallida",
                {"status_zoom": respuesta.status_code},
            )
        if respuesta.status_code in {204, 404} or not respuesta.content:
            return {}
        return respuesta.json()

    def crear_reunion(self, host_user_id, payload):
        if not host_user_id:
            raise ErrorDominio(
                "No se configuró un usuario anfitrión de Zoom para este psicólogo.",
                503,
                "zoom_host_no_configurado",
            )
        return self._solicitud(
            "POST", f"/users/{quote(str(host_user_id), safe='')}/meetings", json=payload
        )

    def actualizar_reunion(self, meeting_id, payload):
        return self._solicitud("PATCH", f"/meetings/{quote(str(meeting_id), safe='')}", json=payload)

    def obtener_reunion(self, meeting_id):
        return self._solicitud("GET", f"/meetings/{quote(str(meeting_id), safe='')}")

    def eliminar_reunion(self, meeting_id):
        return self._solicitud(
            "DELETE",
            f"/meetings/{quote(str(meeting_id), safe='')}",
            codigos_aceptados={204, 404},
        )
