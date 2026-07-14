import requests
from flask import current_app


class NotificadorTeleconsulta:
    @staticmethod
    def _payload(cita, actor_id=None):
        return {
            "actor_id": int(actor_id) if actor_id is not None else None,
            "cita": {
                "id": str(cita.id),
                "paciente_id": cita.paciente_id,
                "psicologo_id": cita.psicologo_id,
                "fecha_hora_inicio": cita.fecha_hora_inicio.isoformat(),
                "fecha_hora_fin": cita.fecha_hora_fin.isoformat(),
                "estado": cita.estado,
                "modalidad": cita.modalidad,
            },
        }

    @staticmethod
    def sincronizar(cita, actor_id=None):
        url = current_app.config.get("TELECONSULTA_SERVICE_URL")
        token = current_app.config.get("TELECONSULTA_INTERNAL_TOKEN")
        if not url or not token:
            current_app.logger.warning("Teleconsulta no configurada; se omitió sincronización de cita %s.", cita.id)
            return False
        try:
            respuesta = requests.post(
                f"{url}/api/teleconsultas/interna/citas/sincronizar",
                json=NotificadorTeleconsulta._payload(cita, actor_id),
                headers={"X-Internal-Token": token},
                timeout=current_app.config.get("TELECONSULTA_TIMEOUT", 5),
            )
            if respuesta.status_code >= 400:
                current_app.logger.warning(
                    "Teleconsulta rechazó sincronización de cita %s: %s %s",
                    cita.id,
                    respuesta.status_code,
                    respuesta.text[:300],
                )
                return False
            return True
        except requests.RequestException as error:
            current_app.logger.warning("No se pudo sincronizar cita %s con teleconsulta: %s", cita.id, error)
            return False
