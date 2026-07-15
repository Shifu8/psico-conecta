import requests
from flask import current_app


class NotificadorPagos:
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
                "reprogramada_desde": (
                    str(cita.reprogramada_desde) if cita.reprogramada_desde else None
                ),
            },
        }

    @staticmethod
    def sincronizar(cita, actor_id=None):
        url = current_app.config.get("PAGOS_SERVICE_URL")
        token = current_app.config.get("PAGOS_INTERNAL_TOKEN")
        if not url or not token:
            current_app.logger.warning(
                "Pagos no configurado; se omitió sincronización de cita %s.", cita.id
            )
            return False
        try:
            respuesta = requests.post(
                f"{url}/api/pagos/interna/citas/sincronizar",
                json=NotificadorPagos._payload(cita, actor_id),
                headers={"X-Internal-Token": token},
                timeout=current_app.config.get("PAGOS_TIMEOUT", 8),
            )
            if respuesta.status_code >= 400:
                current_app.logger.warning(
                    "Pagos rechazó sincronización de cita %s: %s %s",
                    cita.id,
                    respuesta.status_code,
                    respuesta.text[:300],
                )
                return False
            return True
        except requests.RequestException as error:
            current_app.logger.warning(
                "No se pudo sincronizar cita %s con pagos: %s", cita.id, error
            )
            return False
