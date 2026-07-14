from app import db
from app.modelos.cita import Cita
from app.modelos.historial import HistorialCambioCita
from app.servicios.servicio_disponibilidad import (
    ESTADOS_QUE_OCUPAN,
    ServicioDisponibilidad,
)
from app.servicios.servicio_teleconsulta import NotificadorTeleconsulta
from app.utilidades.autenticacion import validar_psicologo_activo
from app.utilidades.errores import ErrorDominio
from app.utilidades.helpers import bloquear_agendas
from app.utilidades.tiempo import asegurar_datetime_utc, ahora_utc


TRANSICIONES = {
    "CONFIRMAR": {"desde": {"PENDIENTE"}, "hacia": "CONFIRMADA"},
    "CANCELAR": {"desde": {"PENDIENTE", "CONFIRMADA"}, "hacia": "CANCELADA"},
    "COMPLETAR": {"desde": {"CONFIRMADA"}, "hacia": "COMPLETADA"},
    "NO_ASISTIDA": {"desde": {"CONFIRMADA"}, "hacia": "NO_ASISTIDA"},
}


class ServicioCita:
    @staticmethod
    def _snapshot(cita):
        return {
            "id": str(cita.id),
            "paciente_id": cita.paciente_id,
            "psicologo_id": cita.psicologo_id,
            "fecha_hora_inicio": cita.fecha_hora_inicio.isoformat(),
            "fecha_hora_fin": cita.fecha_hora_fin.isoformat(),
            "estado": cita.estado,
            "modalidad": cita.modalidad,
            "motivo_consulta": cita.motivo_consulta,
            "notas_psicologo": cita.notas_psicologo,
            "motivo_cancelacion": cita.motivo_cancelacion,
            "cancelado_por": cita.cancelado_por,
            "reprogramada_desde": (
                str(cita.reprogramada_desde) if cita.reprogramada_desde else None
            ),
        }

    @staticmethod
    def registrar_historial(
        cita,
        accion,
        cambiado_por,
        estado_anterior=None,
        motivo=None,
        datos_anteriores=None,
    ):
        registro = HistorialCambioCita(
            cita_id=cita.id,
            accion=accion,
            estado_anterior=estado_anterior,
            estado_nuevo=cita.estado,
            cambiado_por=int(cambiado_por),
            motivo=motivo,
            datos_anteriores=datos_anteriores,
            datos_nuevos=ServicioCita._snapshot(cita),
        )
        db.session.add(registro)
        return registro

    @staticmethod
    def _obtener_bloqueada(cita_id):
        cita = Cita.query.filter_by(id=cita_id).with_for_update().first()
        if not cita:
            raise ErrorDominio("Cita no encontrada.", 404, "cita_no_encontrada")
        return cita

    @staticmethod
    def obtener(cita_id):
        cita = db.session.get(Cita, cita_id)
        if not cita:
            raise ErrorDominio("Cita no encontrada.", 404, "cita_no_encontrada")
        return cita

    @staticmethod
    def verificar_acceso(cita, usuario_id, rol):
        usuario_id = int(usuario_id)
        if rol == "ADMIN":
            return
        if rol == "PACIENTE" and cita.paciente_id == usuario_id:
            return
        if rol == "PSICOLOGO" and cita.psicologo_id == usuario_id:
            return
        raise ErrorDominio(
            "No tienes acceso a esta cita.", 403, "acceso_denegado"
        )

    @staticmethod
    def _validar_sin_solapamientos(
        paciente_id, psicologo_id, inicio, fin, excluir_cita_id=None
    ):
        consulta_psicologo = Cita.query.filter(
            Cita.psicologo_id == int(psicologo_id),
            Cita.estado.in_(ESTADOS_QUE_OCUPAN),
            Cita.fecha_hora_inicio < fin,
            Cita.fecha_hora_fin > inicio,
        )
        consulta_paciente = Cita.query.filter(
            Cita.paciente_id == int(paciente_id),
            Cita.estado.in_(ESTADOS_QUE_OCUPAN),
            Cita.fecha_hora_inicio < fin,
            Cita.fecha_hora_fin > inicio,
        )
        if excluir_cita_id:
            consulta_psicologo = consulta_psicologo.filter(Cita.id != excluir_cita_id)
            consulta_paciente = consulta_paciente.filter(Cita.id != excluir_cita_id)

        if consulta_psicologo.first():
            raise ErrorDominio(
                "El horario seleccionado ya fue reservado con este profesional.",
                409,
                "horario_ocupado",
            )
        if consulta_paciente.first():
            raise ErrorDominio(
                "Ya tienes otra cita que coincide con ese horario.",
                409,
                "paciente_con_cita_solapada",
            )

    @staticmethod
    def agendar_cita(paciente_id, datos):
        paciente_id = int(paciente_id)
        psicologo_id = int(datos["psicologo_id"])
        inicio = asegurar_datetime_utc(datos["fecha_hora_inicio"])
        if inicio <= ahora_utc():
            raise ErrorDominio("No se pueden agendar citas en el pasado.")

        validar_psicologo_activo(psicologo_id)
        bloquear_agendas(psicologo_id, paciente_id)
        _bloque, fin = ServicioDisponibilidad.obtener_bloque_para_slot(
            psicologo_id, inicio
        )
        ServicioCita._validar_sin_solapamientos(
            paciente_id, psicologo_id, inicio, fin
        )

        cita = Cita(
            paciente_id=paciente_id,
            psicologo_id=psicologo_id,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin,
            estado="PENDIENTE",
            modalidad=datos.get("modalidad", "VIRTUAL"),
            motivo_consulta=datos.get("motivo_consulta"),
        )
        db.session.add(cita)
        db.session.flush()
        ServicioCita.registrar_historial(
            cita,
            "CREACION",
            paciente_id,
            estado_anterior=None,
            motivo="Creación de cita",
        )
        db.session.commit()
        return cita

    @staticmethod
    def cambiar_estado(cita_id, accion, usuario_id, rol, motivo=None):
        usuario_id = int(usuario_id)
        cita = ServicioCita._obtener_bloqueada(cita_id)
        ServicioCita.verificar_acceso(cita, usuario_id, rol)

        regla = TRANSICIONES[accion]
        if cita.estado not in regla["desde"]:
            raise ErrorDominio(
                f"No se puede ejecutar esta acción cuando la cita está en estado {cita.estado}.",
                409,
                "transicion_estado_invalida",
            )

        ahora = ahora_utc()
        inicio = asegurar_datetime_utc(cita.fecha_hora_inicio, False)
        fin = asegurar_datetime_utc(cita.fecha_hora_fin, False)

        if accion == "CONFIRMAR":
            if rol != "PSICOLOGO" or cita.psicologo_id != usuario_id:
                raise ErrorDominio(
                    "Solo el psicólogo asignado puede confirmar la cita.",
                    403,
                    "acceso_denegado",
                )
            if inicio <= ahora:
                raise ErrorDominio(
                    "No se puede confirmar una cita que ya comenzó.",
                    409,
                    "cita_iniciada",
                )

        if accion == "CANCELAR":
            if inicio <= ahora:
                raise ErrorDominio(
                    "Una cita que ya comenzó no puede cancelarse; debe completarse o marcarse como no asistida.",
                    409,
                    "cita_iniciada",
                )
            if not motivo:
                raise ErrorDominio("Debes indicar el motivo de cancelación.")

        if accion in {"COMPLETAR", "NO_ASISTIDA"}:
            if rol != "PSICOLOGO" or cita.psicologo_id != usuario_id:
                raise ErrorDominio(
                    "Solo el psicólogo asignado puede cerrar la cita.",
                    403,
                    "acceso_denegado",
                )
            if fin > ahora:
                raise ErrorDominio(
                    "La cita aún no ha finalizado.",
                    409,
                    "cita_no_finalizada",
                )

        anterior = ServicioCita._snapshot(cita)
        estado_anterior = cita.estado
        cita.estado = regla["hacia"]
        if accion == "CANCELAR":
            cita.cancelado_por = usuario_id
            cita.motivo_cancelacion = motivo
        cita.fecha_actualizacion = ahora
        ServicioCita.registrar_historial(
            cita,
            accion,
            usuario_id,
            estado_anterior=estado_anterior,
            motivo=motivo,
            datos_anteriores=anterior,
        )
        db.session.commit()
        NotificadorTeleconsulta.sincronizar(cita, usuario_id)
        return cita

    @staticmethod
    def reprogramar(cita_id, nueva_fecha, usuario_id, rol):
        usuario_id = int(usuario_id)
        cita_anterior = ServicioCita._obtener_bloqueada(cita_id)
        ServicioCita.verificar_acceso(cita_anterior, usuario_id, rol)
        if cita_anterior.estado not in {"PENDIENTE", "CONFIRMADA"}:
            raise ErrorDominio(
                "Solo se pueden reprogramar citas pendientes o confirmadas.",
                409,
                "transicion_estado_invalida",
            )

        inicio_actual = asegurar_datetime_utc(cita_anterior.fecha_hora_inicio, False)
        if inicio_actual <= ahora_utc():
            raise ErrorDominio(
                "No se puede reprogramar una cita que ya comenzó.",
                409,
                "cita_iniciada",
            )

        nuevo_inicio = asegurar_datetime_utc(nueva_fecha)
        if nuevo_inicio <= ahora_utc():
            raise ErrorDominio("La nueva fecha debe estar en el futuro.")
        if nuevo_inicio == inicio_actual:
            raise ErrorDominio("Selecciona un horario diferente al actual.")

        bloquear_agendas(cita_anterior.psicologo_id, cita_anterior.paciente_id)
        _bloque, nuevo_fin = ServicioDisponibilidad.obtener_bloque_para_slot(
            cita_anterior.psicologo_id, nuevo_inicio
        )
        ServicioCita._validar_sin_solapamientos(
            cita_anterior.paciente_id,
            cita_anterior.psicologo_id,
            nuevo_inicio,
            nuevo_fin,
            excluir_cita_id=cita_anterior.id,
        )

        snapshot_anterior = ServicioCita._snapshot(cita_anterior)
        estado_previo = cita_anterior.estado
        cita_anterior.estado = "REPROGRAMADA"
        cita_anterior.fecha_actualizacion = ahora_utc()
        ServicioCita.registrar_historial(
            cita_anterior,
            "REPROGRAMAR_ORIGEN",
            usuario_id,
            estado_anterior=estado_previo,
            motivo="La cita fue reemplazada por una nueva fecha.",
            datos_anteriores=snapshot_anterior,
        )

        nueva_cita = Cita(
            paciente_id=cita_anterior.paciente_id,
            psicologo_id=cita_anterior.psicologo_id,
            fecha_hora_inicio=nuevo_inicio,
            fecha_hora_fin=nuevo_fin,
            estado="PENDIENTE",
            modalidad=cita_anterior.modalidad,
            motivo_consulta=cita_anterior.motivo_consulta,
            reprogramada_desde=cita_anterior.id,
        )
        db.session.add(nueva_cita)
        db.session.flush()
        ServicioCita.registrar_historial(
            nueva_cita,
            "REPROGRAMAR_DESTINO",
            usuario_id,
            estado_anterior=None,
            motivo=f"Cita creada al reprogramar {cita_anterior.id}.",
        )
        db.session.commit()
        NotificadorTeleconsulta.sincronizar(cita_anterior, usuario_id)
        NotificadorTeleconsulta.sincronizar(nueva_cita, usuario_id)
        return nueva_cita

    @staticmethod
    def actualizar_notas(cita_id, notas, usuario_id, rol):
        usuario_id = int(usuario_id)
        cita = ServicioCita._obtener_bloqueada(cita_id)
        if rol != "PSICOLOGO" or cita.psicologo_id != usuario_id:
            raise ErrorDominio(
                "Solo el psicólogo asignado puede editar las notas.",
                403,
                "acceso_denegado",
            )
        if cita.estado in {"CANCELADA", "REPROGRAMADA"}:
            raise ErrorDominio(
                "No se pueden editar notas de una cita cancelada o reemplazada.",
                409,
                "estado_invalido",
            )

        anterior = ServicioCita._snapshot(cita)
        cita.notas_psicologo = notas.strip()
        cita.fecha_actualizacion = ahora_utc()
        ServicioCita.registrar_historial(
            cita,
            "ACTUALIZAR_NOTAS",
            usuario_id,
            estado_anterior=cita.estado,
            motivo="Actualización de notas del profesional.",
            datos_anteriores=anterior,
        )
        db.session.commit()
        return cita

    @staticmethod
    def historial(cita_id):
        return (
            HistorialCambioCita.query.filter_by(cita_id=cita_id)
            .order_by(HistorialCambioCita.fecha_cambio.asc())
            .all()
        )
