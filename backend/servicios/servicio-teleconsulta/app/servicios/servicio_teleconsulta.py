import math
import uuid
from datetime import timedelta

from flask import current_app

from sqlalchemy import text

from app import db
from app.modelos import HistorialSesion, SesionZoom
from app.servicios.cliente_zoom import ClienteZoom
from app.utilidades.errores import ErrorDominio
from app.utilidades.tiempo import ahora_utc, asegurar_utc, iso_zoom


ESTADOS_CITA_TERMINALES = {"CANCELADA", "REPROGRAMADA"}


class ServicioTeleconsulta:
    @staticmethod
    def cliente_zoom():
        cliente = current_app.extensions.get("zoom_client")
        if cliente is None:
            cliente = ClienteZoom()
            current_app.extensions["zoom_client"] = cliente
        return cliente

    @staticmethod
    def _bloquear_cita(cita_id):
        if db.engine.dialect.name != "postgresql":
            return
        # Evita que dos procesos creen dos reuniones Zoom para la misma cita.
        clave = int(cita_id.int & ((1 << 63) - 1))
        db.session.execute(text("SELECT pg_advisory_xact_lock(:clave)"), {"clave": clave})

    @staticmethod
    def _registrar(sesion, evento, actor_id=None, data=None):
        db.session.add(HistorialSesion(
            sesion_id=sesion.id,
            evento=evento,
            actor_id=int(actor_id) if actor_id is not None else None,
            data=data or {},
        ))

    @staticmethod
    def _cita_normalizada(cita):
        try:
            return {
                "id": uuid.UUID(str(cita["id"])),
                "paciente_id": int(cita["paciente_id"]),
                "psicologo_id": int(cita["psicologo_id"]),
                "inicio": asegurar_utc(cita["fecha_hora_inicio"]),
                "fin": asegurar_utc(cita["fecha_hora_fin"]),
                "estado": str(cita["estado"]).upper(),
                "modalidad": str(cita["modalidad"]).upper(),
            }
        except (KeyError, TypeError, ValueError):
            raise ErrorDominio("Los datos de la cita son incompletos.", 400, "cita_invalida") from None

    @staticmethod
    def _payload_zoom(cita):
        duracion = max(1, math.ceil((cita["fin"] - cita["inicio"]).total_seconds() / 60))
        return {
            "topic": "Teleconsulta PsicoConecta",
            "type": 2,
            "start_time": iso_zoom(cita["inicio"]),
            "duration": duracion,
            "timezone": current_app.config["TIMEZONE"],
            "agenda": f"Sesión privada asociada a la cita {str(cita['id'])[:8]}.",
            "default_password": True,
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "waiting_room": True,
                "mute_upon_entry": True,
                "audio": "both",
                "auto_recording": "none",
                "use_pmi": False,
                "email_notification": False,
            },
        }

    @staticmethod
    def _cancelar_en_zoom(sesion):
        if not sesion.zoom_meeting_id:
            return True
        try:
            ServicioTeleconsulta.cliente_zoom().eliminar_reunion(sesion.zoom_meeting_id)
            sesion.zoom_meeting_id = None
            sesion.zoom_meeting_uuid = None
            sesion.zoom_host_user_id = None
            sesion.enlace_acceso = None
            sesion.contrasena = None
            current_app.logger.info(
                "Reunión Zoom eliminada para sesión %s.", sesion.id
            )
            return True
        except ErrorDominio as error:
            # Se conserva el ID para reintentar la eliminación en la siguiente sincronización.
            sesion.ultimo_error = error.mensaje
            return False

    @staticmethod
    def sincronizar_desde_cita(cita_raw, actor_id=None):
        cita = ServicioTeleconsulta._cita_normalizada(cita_raw)
        ServicioTeleconsulta._bloquear_cita(cita["id"])
        sesion = (
            SesionZoom.query.filter_by(cita_id=cita["id"]).with_for_update().first()
        )

        elegible = cita["modalidad"] == "VIRTUAL" and cita["estado"] == "CONFIRMADA"
        if not elegible:
            if not sesion:
                return None
            estado_previo = sesion.estado
            sesion.paciente_id = cita["paciente_id"]
            sesion.psicologo_id = cita["psicologo_id"]
            sesion.fecha_hora_inicio = cita["inicio"]
            sesion.fecha_hora_fin = cita["fin"]
            if cita["estado"] in ESTADOS_CITA_TERMINALES or cita["modalidad"] != "VIRTUAL":
                ServicioTeleconsulta._cancelar_en_zoom(sesion)
                sesion.estado = "CANCELADA"
                sesion.enlace_acceso = None
            elif cita["estado"] in {"COMPLETADA", "NO_ASISTIDA"}:
                sesion.estado = "FINALIZADA"
            ServicioTeleconsulta._registrar(
                sesion,
                "SINCRONIZACION_ESTADO",
                actor_id,
                {"estado_anterior": estado_previo, "estado_cita": cita["estado"]},
            )
            sesion.actualizado_en = ahora_utc()
            db.session.commit()
            return sesion

        nueva = sesion is None
        if nueva:
            sesion = SesionZoom(
                cita_id=cita["id"],
                paciente_id=cita["paciente_id"],
                psicologo_id=cita["psicologo_id"],
                fecha_hora_inicio=cita["inicio"],
                fecha_hora_fin=cita["fin"],
                tema="Teleconsulta PsicoConecta",
                estado="PROGRAMADA",
            )
            db.session.add(sesion)
            db.session.flush()

        zoom = ServicioTeleconsulta.cliente_zoom()
        host = zoom.resolver_host(cita["psicologo_id"])
        if not host:
            sesion.estado = "ERROR"
            sesion.ultimo_error = "No se configuró el anfitrión Zoom del psicólogo."
            sesion.actualizado_en = ahora_utc()
            ServicioTeleconsulta._registrar(
                sesion,
                "ERROR_ZOOM",
                actor_id,
                {"mensaje": sesion.ultimo_error},
            )
            db.session.commit()
            raise ErrorDominio(
                sesion.ultimo_error,
                503,
                "zoom_host_no_configurado",
            )

        cambio_horario = (
            asegurar_utc(sesion.fecha_hora_inicio) != cita["inicio"]
            or asegurar_utc(sesion.fecha_hora_fin) != cita["fin"]
        )
        cambio_host = bool(sesion.zoom_host_user_id and sesion.zoom_host_user_id != host)

        sesion.paciente_id = cita["paciente_id"]
        sesion.psicologo_id = cita["psicologo_id"]
        sesion.fecha_hora_inicio = cita["inicio"]
        sesion.fecha_hora_fin = cita["fin"]
        sesion.zoom_host_user_id = host

        try:
            if not sesion.zoom_meeting_id or cambio_host:
                if cambio_host and sesion.zoom_meeting_id:
                    ServicioTeleconsulta._cancelar_en_zoom(sesion)
                respuesta = zoom.crear_reunion(host, ServicioTeleconsulta._payload_zoom(cita))
                sesion.zoom_meeting_id = str(respuesta["id"])
                sesion.zoom_meeting_uuid = respuesta.get("uuid")
                sesion.enlace_acceso = respuesta.get("join_url")
                sesion.contrasena = respuesta.get("password")
                evento = "REUNION_ZOOM_CREADA"
                current_app.logger.info(
                    "Reunión Zoom %s creada para cita %s.",
                    sesion.zoom_meeting_id,
                    sesion.cita_id,
                )
            elif cambio_horario:
                zoom.actualizar_reunion(sesion.zoom_meeting_id, ServicioTeleconsulta._payload_zoom(cita))
                respuesta = zoom.obtener_reunion(sesion.zoom_meeting_id)
                sesion.enlace_acceso = respuesta.get("join_url") or sesion.enlace_acceso
                sesion.contrasena = respuesta.get("password") or sesion.contrasena
                evento = "REUNION_ZOOM_ACTUALIZADA"
                current_app.logger.info(
                    "Reunión Zoom %s actualizada para cita %s.",
                    sesion.zoom_meeting_id,
                    sesion.cita_id,
                )
            else:
                evento = "SESION_VERIFICADA"
            sesion.estado = "PROGRAMADA"
            sesion.ultimo_error = None
            sesion.ultima_sincronizacion_zoom = ahora_utc()
            sesion.actualizado_en = ahora_utc()
            ServicioTeleconsulta._registrar(sesion, evento, actor_id, {"host": host})
            db.session.commit()
            return sesion
        except ErrorDominio as error:
            sesion.estado = "ERROR"
            sesion.ultimo_error = error.mensaje
            sesion.actualizado_en = ahora_utc()
            ServicioTeleconsulta._registrar(sesion, "ERROR_ZOOM", actor_id, {"mensaje": error.mensaje})
            db.session.commit()
            current_app.logger.warning(
                "No se pudo sincronizar Zoom para cita %s: %s",
                sesion.cita_id,
                error.mensaje,
            )
            raise

    @staticmethod
    def verificar_propiedad(cita, usuario_id, rol):
        usuario_id = int(usuario_id)
        if rol == "PACIENTE" and int(cita["paciente_id"]) == usuario_id:
            return
        if rol == "PSICOLOGO" and int(cita["psicologo_id"]) == usuario_id:
            return
        if rol == "ADMIN":
            return
        raise ErrorDominio("No tienes acceso a esta teleconsulta.", 403, "acceso_denegado")

    @staticmethod
    def estado_acceso(sesion, rol, ahora=None):
        ahora = asegurar_utc(ahora or ahora_utc())
        inicio = asegurar_utc(sesion.fecha_hora_inicio)
        fin = asegurar_utc(sesion.fecha_hora_fin)
        minutos = (
            current_app.config["ACCESO_ANTES_PSICOLOGO_MIN"]
            if rol == "PSICOLOGO"
            else current_app.config["ACCESO_ANTES_PACIENTE_MIN"]
        )
        disponible_desde = inicio - timedelta(minutes=minutos)
        disponible_hasta = fin + timedelta(minutes=current_app.config["ACCESO_DESPUES_FIN_MIN"])
        if sesion.estado in {"CANCELADA", "FINALIZADA"}:
            return False, disponible_desde, "La teleconsulta ya no está disponible."
        if sesion.estado == "ERROR":
            return False, disponible_desde, sesion.ultimo_error or "La reunión de Zoom no pudo prepararse."
        if ahora < disponible_desde:
            return False, disponible_desde, "El acceso se habilitará poco antes de la hora acordada."
        if ahora > disponible_hasta:
            return False, disponible_desde, "El periodo de acceso a la teleconsulta finalizó."
        return True, disponible_desde, None

    @staticmethod
    def serializar(sesion, rol, ahora=None):
        puede, desde, mensaje = ServicioTeleconsulta.estado_acceso(sesion, rol, ahora)
        return {
            "id": sesion.id,
            "cita_id": sesion.cita_id,
            "paciente_id": sesion.paciente_id,
            "psicologo_id": sesion.psicologo_id,
            "tema": sesion.tema,
            "fecha_hora_inicio": sesion.fecha_hora_inicio,
            "fecha_hora_fin": sesion.fecha_hora_fin,
            "estado": sesion.estado,
            "zoom_configurada": bool(sesion.zoom_meeting_id and sesion.enlace_acceso),
            "puede_ingresar": puede,
            "disponible_desde": desde,
            "mensaje_acceso": mensaje or sesion.ultimo_error,
        }

    @staticmethod
    def obtener_acceso(sesion, rol):
        if sesion.estado == "ERROR":
            raise ErrorDominio(
                sesion.ultimo_error or "La reunión de Zoom no pudo prepararse.",
                503,
                "reunion_no_disponible",
            )
        puede, disponible_desde, mensaje = ServicioTeleconsulta.estado_acceso(sesion, rol)
        if not puede:
            codigo = 403 if ahora_utc() < disponible_desde else 410
            raise ErrorDominio(
                mensaje,
                codigo,
                "acceso_fuera_de_horario",
                {"disponible_desde": disponible_desde.isoformat()},
            )
        if not sesion.zoom_meeting_id:
            raise ErrorDominio("La reunión de Zoom todavía no está disponible.", 503, "reunion_no_disponible")
        if rol == "PACIENTE":
            if not sesion.enlace_acceso:
                raise ErrorDominio("El enlace de la reunión no está disponible.", 503, "reunion_no_disponible")
            return {"cita_id": sesion.cita_id, "rol": rol, "url": sesion.enlace_acceso, "expira_en": None}
        if rol == "PSICOLOGO":
            reunion = ServicioTeleconsulta.cliente_zoom().obtener_reunion(sesion.zoom_meeting_id)
            url = reunion.get("start_url")
            if not url:
                raise ErrorDominio("Zoom no devolvió un enlace de anfitrión.", 503, "enlace_anfitrion_no_disponible")
            return {
                "cita_id": sesion.cita_id,
                "rol": rol,
                "url": url,
                "expira_en": ahora_utc() + timedelta(hours=2),
            }
        raise ErrorDominio("El administrador no puede ingresar a una sesión clínica.", 403, "acceso_denegado")
