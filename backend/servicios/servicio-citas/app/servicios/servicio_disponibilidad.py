from datetime import datetime, time
from types import SimpleNamespace

from sqlalchemy import or_

from app import db
from app.modelos.cita import Cita
from app.modelos.disponibilidad import Disponibilidad, ExcepcionDisponibilidad
from app.utilidades.errores import ErrorDominio
from app.utilidades.helpers import bloquear_agendas, generar_slots
from app.utilidades.tiempo import (
    asegurar_datetime_utc,
    a_hora_local,
    ahora_utc,
    combinar_fecha_hora_local,
    fecha_local_actual,
    limites_dia_utc,
)


ESTADOS_QUE_OCUPAN = ("PENDIENTE", "CONFIRMADA")

# La agenda semanal es una regla del sistema. El administrador únicamente
# registra excepciones para fechas no disponibles. Estos bloques también sirven
# como respaldo para psicólogos nuevos que aún no tengan filas persistidas.
HORARIO_BASE = {
    dia: (
        (time(8, 0), time(12, 0), 50),
        (time(14, 0), time(17, 0), 50),
    )
    for dia in range(5)
}


def _bloques_base(psicologo_id, dia_semana):
    return [
        SimpleNamespace(
            id=None,
            psicologo_id=int(psicologo_id),
            dia_semana=dia_semana,
            hora_inicio=inicio,
            hora_fin=fin,
            duracion_slot=duracion,
            activo=True,
        )
        for inicio, fin, duracion in HORARIO_BASE.get(dia_semana, ())
    ]


class ServicioDisponibilidad:
    @staticmethod
    def obtener_disponibilidad(psicologo_id):
        return (
            Disponibilidad.query.filter_by(psicologo_id=int(psicologo_id))
            .order_by(Disponibilidad.dia_semana, Disponibilidad.hora_inicio)
            .all()
        )

    @staticmethod
    def _validar_solapamiento(psicologo_id, dia_semana, inicio, fin, excluir_id=None):
        consulta = Disponibilidad.query.filter(
            Disponibilidad.psicologo_id == int(psicologo_id),
            Disponibilidad.dia_semana == dia_semana,
            Disponibilidad.activo.is_(True),
            Disponibilidad.hora_inicio < fin,
            Disponibilidad.hora_fin > inicio,
        )
        if excluir_id:
            consulta = consulta.filter(Disponibilidad.id != excluir_id)
        if consulta.first():
            raise ErrorDominio(
                "El bloque se solapa con otro horario activo del profesional.",
                409,
                "disponibilidad_solapada",
            )

    @staticmethod
    def crear_bloque(psicologo_id, datos):
        psicologo_id = int(psicologo_id)
        bloquear_agendas(psicologo_id)
        ServicioDisponibilidad._validar_solapamiento(
            psicologo_id,
            datos["dia_semana"],
            datos["hora_inicio"],
            datos["hora_fin"],
        )
        bloque = Disponibilidad(
            psicologo_id=psicologo_id,
            dia_semana=datos["dia_semana"],
            hora_inicio=datos["hora_inicio"],
            hora_fin=datos["hora_fin"],
            duracion_slot=datos.get("duracion_slot", 50),
            activo=True,
        )
        db.session.add(bloque)
        db.session.commit()
        return bloque

    @staticmethod
    def _bloque_cubre_cita(bloque, cita):
        if not bloque.activo:
            return False
        inicio_local = a_hora_local(cita.fecha_hora_inicio)
        fin_local = a_hora_local(cita.fecha_hora_fin)
        if inicio_local.date() != fin_local.date():
            return False
        if inicio_local.weekday() != bloque.dia_semana:
            return False
        for slot in generar_slots(
            bloque.hora_inicio, bloque.hora_fin, bloque.duracion_slot
        ):
            if (
                inicio_local.time().replace(tzinfo=None) == slot["hora_inicio"]
                and fin_local.time().replace(tzinfo=None) == slot["hora_fin"]
            ):
                return True
        return False

    @staticmethod
    def _validar_citas_siguen_cubiertas(citas_afectadas, bloques_resultantes):
        invalidas = [
            str(cita.id)
            for cita in citas_afectadas
            if not any(
                ServicioDisponibilidad._bloque_cubre_cita(bloque, cita)
                for bloque in bloques_resultantes
            )
        ]
        if invalidas:
            raise ErrorDominio(
                "El cambio dejaría citas futuras fuera de la disponibilidad configurada. "
                "Reprograma o cancela esas citas antes de modificar el bloque.",
                409,
                "citas_fuera_de_disponibilidad",
                {"citas": invalidas},
            )

    @staticmethod
    def actualizar_bloque(bloque_id, psicologo_id, datos):
        psicologo_id = int(psicologo_id)
        bloquear_agendas(psicologo_id)
        bloque = Disponibilidad.query.filter_by(
            id=bloque_id, psicologo_id=psicologo_id
        ).with_for_update().first()
        if not bloque:
            raise ErrorDominio("Bloque de disponibilidad no encontrado.", 404, "no_encontrado")
        if not datos:
            raise ErrorDominio("Envía al menos un campo para actualizar.")

        nuevos = {
            "dia_semana": datos.get("dia_semana", bloque.dia_semana),
            "hora_inicio": datos.get("hora_inicio", bloque.hora_inicio),
            "hora_fin": datos.get("hora_fin", bloque.hora_fin),
            "duracion_slot": datos.get("duracion_slot", bloque.duracion_slot),
            "activo": datos.get("activo", bloque.activo),
        }
        if nuevos["hora_fin"] <= nuevos["hora_inicio"]:
            raise ErrorDominio("La hora final debe ser posterior a la hora inicial.")
        if nuevos["activo"]:
            ServicioDisponibilidad._validar_solapamiento(
                psicologo_id,
                nuevos["dia_semana"],
                nuevos["hora_inicio"],
                nuevos["hora_fin"],
                bloque.id,
            )

        citas_futuras = Cita.query.filter(
            Cita.psicologo_id == psicologo_id,
            Cita.estado.in_(ESTADOS_QUE_OCUPAN),
            Cita.fecha_hora_inicio > ahora_utc(),
        ).all()
        citas_afectadas = [
            cita for cita in citas_futuras
            if ServicioDisponibilidad._bloque_cubre_cita(bloque, cita)
        ]
        bloques = Disponibilidad.query.filter_by(psicologo_id=psicologo_id).all()
        for clave, valor in nuevos.items():
            setattr(bloque, clave, valor)
        bloque.fecha_actualizacion = ahora_utc()
        ServicioDisponibilidad._validar_citas_siguen_cubiertas(
            citas_afectadas, bloques
        )
        db.session.commit()
        return bloque

    @staticmethod
    def eliminar_bloque(bloque_id, psicologo_id):
        psicologo_id = int(psicologo_id)
        bloquear_agendas(psicologo_id)
        bloque = Disponibilidad.query.filter_by(
            id=bloque_id, psicologo_id=psicologo_id
        ).with_for_update().first()
        if not bloque:
            raise ErrorDominio("Bloque de disponibilidad no encontrado.", 404, "no_encontrado")

        citas_futuras = Cita.query.filter(
            Cita.psicologo_id == psicologo_id,
            Cita.estado.in_(ESTADOS_QUE_OCUPAN),
            Cita.fecha_hora_inicio > ahora_utc(),
        ).all()
        citas_afectadas = [
            cita for cita in citas_futuras
            if ServicioDisponibilidad._bloque_cubre_cita(bloque, cita)
        ]
        bloques_restantes = Disponibilidad.query.filter(
            Disponibilidad.psicologo_id == psicologo_id,
            Disponibilidad.id != bloque.id,
        ).all()
        ServicioDisponibilidad._validar_citas_siguen_cubiertas(
            citas_afectadas, bloques_restantes
        )
        db.session.delete(bloque)
        db.session.commit()

    @staticmethod
    def crear_excepcion(psicologo_id, datos):
        psicologo_id = int(psicologo_id)
        fecha = datos["fecha"]
        if fecha < fecha_local_actual():
            raise ErrorDominio("No se puede bloquear una fecha pasada.")

        bloquear_agendas(psicologo_id)
        if ExcepcionDisponibilidad.query.filter_by(
            psicologo_id=psicologo_id, fecha=fecha
        ).first():
            raise ErrorDominio(
                "La fecha ya está bloqueada para este profesional.",
                409,
                "excepcion_duplicada",
            )

        inicio, fin = limites_dia_utc(fecha)
        citas = Cita.query.filter(
            Cita.psicologo_id == psicologo_id,
            Cita.estado.in_(ESTADOS_QUE_OCUPAN),
            Cita.fecha_hora_inicio >= inicio,
            Cita.fecha_hora_inicio <= fin,
        ).all()
        if citas:
            raise ErrorDominio(
                "La fecha tiene citas activas. Reprográmalas o cancélalas antes de bloquearla.",
                409,
                "fecha_con_citas",
                {"citas": [str(cita.id) for cita in citas]},
            )

        excepcion = ExcepcionDisponibilidad(
            psicologo_id=psicologo_id,
            fecha=fecha,
            motivo=datos.get("motivo"),
        )
        db.session.add(excepcion)
        db.session.commit()
        return excepcion

    @staticmethod
    def obtener_excepciones(psicologo_id):
        return (
            ExcepcionDisponibilidad.query.filter_by(psicologo_id=int(psicologo_id))
            .order_by(ExcepcionDisponibilidad.fecha)
            .all()
        )

    @staticmethod
    def obtener_excepcion(excepcion_id):
        excepcion = db.session.get(ExcepcionDisponibilidad, excepcion_id)
        if not excepcion:
            raise ErrorDominio("Excepción no encontrada.", 404, "no_encontrado")
        return excepcion

    @staticmethod
    def eliminar_excepcion(excepcion_id):
        excepcion = ServicioDisponibilidad.obtener_excepcion(excepcion_id)
        bloquear_agendas(excepcion.psicologo_id)
        db.session.delete(excepcion)
        db.session.commit()

    @staticmethod
    def obtener_bloque_para_slot(psicologo_id, fecha_inicio_utc):
        psicologo_id = int(psicologo_id)
        inicio_local = a_hora_local(fecha_inicio_utc)
        fecha = inicio_local.date()

        if ExcepcionDisponibilidad.query.filter_by(
            psicologo_id=psicologo_id, fecha=fecha
        ).first():
            raise ErrorDominio(
                "El profesional no está disponible en la fecha seleccionada.",
                409,
                "fecha_bloqueada",
            )

        bloques = Disponibilidad.query.filter_by(
            psicologo_id=psicologo_id,
            dia_semana=inicio_local.weekday(),
            activo=True,
        ).all()
        if not bloques:
            bloques = _bloques_base(psicologo_id, inicio_local.weekday())
        for bloque in bloques:
            for slot in generar_slots(
                bloque.hora_inicio, bloque.hora_fin, bloque.duracion_slot
            ):
                if inicio_local.time().replace(tzinfo=None) == slot["hora_inicio"]:
                    fin_local = combinar_fecha_hora_local(fecha, slot["hora_fin"])
                    return bloque, asegurar_datetime_utc(fin_local)

        raise ErrorDominio(
            "El horario seleccionado no corresponde a un espacio disponible del profesional.",
            409,
            "slot_no_disponible",
        )

    @staticmethod
    def obtener_slots_disponibles(psicologo_id, fecha_texto):
        try:
            fecha = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            raise ErrorDominio(
                "Formato de fecha inválido. Usa YYYY-MM-DD.", 400, "fecha_invalida"
            ) from None

        psicologo_id = int(psicologo_id)
        if ExcepcionDisponibilidad.query.filter_by(
            psicologo_id=psicologo_id, fecha=fecha
        ).first():
            return []

        bloques = (
            Disponibilidad.query.filter_by(
                psicologo_id=psicologo_id,
                dia_semana=fecha.weekday(),
                activo=True,
            )
            .order_by(Disponibilidad.hora_inicio)
            .all()
        )
        if not bloques:
            bloques = _bloques_base(psicologo_id, fecha.weekday())
        if not bloques:
            return []

        inicio_dia, fin_dia = limites_dia_utc(fecha)
        citas = Cita.query.filter(
            Cita.psicologo_id == psicologo_id,
            Cita.estado.in_(ESTADOS_QUE_OCUPAN),
            Cita.fecha_hora_inicio <= fin_dia,
            Cita.fecha_hora_fin >= inicio_dia,
        ).all()

        ahora = ahora_utc()
        resultado = []
        for bloque in bloques:
            for slot in generar_slots(
                bloque.hora_inicio, bloque.hora_fin, bloque.duracion_slot
            ):
                inicio_local = combinar_fecha_hora_local(fecha, slot["hora_inicio"])
                fin_local = combinar_fecha_hora_local(fecha, slot["hora_fin"])
                inicio_utc = inicio_local.astimezone(ahora.tzinfo)
                fin_utc = fin_local.astimezone(ahora.tzinfo)
                ocupado = any(
                    asegurar_datetime_utc(cita.fecha_hora_inicio, False) < fin_utc
                    and asegurar_datetime_utc(cita.fecha_hora_fin, False) > inicio_utc
                    for cita in citas
                )
                resultado.append(
                    {
                        "hora_inicio": slot["hora_inicio"].isoformat(),
                        "hora_fin": slot["hora_fin"].isoformat(),
                        "fecha_hora_inicio": inicio_utc.isoformat(),
                        "fecha_hora_fin": fin_utc.isoformat(),
                        "duracion_slot": bloque.duracion_slot,
                        "disponible": inicio_utc > ahora and not ocupado,
                    }
                )
        return resultado
