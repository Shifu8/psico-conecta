# Archivo: servicio_disponibilidad.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Citas

from app import db
from app.modelos.disponibilidad import Disponibilidad, ExcepcionDisponibilidad
from app.modelos.cita import Cita
from app.utilidades.helpers import generar_slots
from sqlalchemy import and_
from datetime import datetime, time, timedelta

# ---------------------------------------------------------------------------
# Horario fijo por defecto para todos los psicólogos.
# Se usa cuando el psicólogo NO tiene bloques personalizados en la BD.
# ---------------------------------------------------------------------------
HORARIO_FIJO_MANANA = (time(8, 0), time(12, 0))
HORARIO_FIJO_TARDE = (time(14, 0), time(17, 0))
DURACION_SLOT_MINUTOS = 60


class ServicioDisponibilidad:
    @staticmethod
    def obtener_disponibilidad(psicologo_id):
        return Disponibilidad.query.filter_by(psicologo_id=psicologo_id).all()

    @staticmethod
    def crear_bloque(psicologo_id, data):
        # Validar solapamientos (simplificado)
        nuevo_bloque = Disponibilidad(
            psicologo_id=psicologo_id,
            dia_semana=data['dia_semana'],
            hora_inicio=data['hora_inicio'],
            hora_fin=data['hora_fin'],
            duracion_slot=data.get('duracion_slot', DURACION_SLOT_MINUTOS)
        )
        db.session.add(nuevo_bloque)
        db.session.commit()
        return nuevo_bloque

    @staticmethod
    def actualizar_bloque(bloque_id, psicologo_id, data):
        bloque = Disponibilidad.query.filter_by(id=bloque_id, psicologo_id=psicologo_id).first()
        if not bloque:
            return None
        
        if 'hora_inicio' in data: bloque.hora_inicio = data['hora_inicio']
        if 'hora_fin' in data: bloque.hora_fin = data['hora_fin']
        if 'duracion_slot' in data: bloque.duracion_slot = data['duracion_slot']
        if 'activo' in data: bloque.activo = data['activo']
        
        db.session.commit()
        return bloque

    @staticmethod
    def eliminar_bloque(bloque_id, psicologo_id):
        bloque = Disponibilidad.query.filter_by(id=bloque_id, psicologo_id=psicologo_id).first()
        if not bloque:
            return False
        db.session.delete(bloque)
        db.session.commit()
        return True

    @staticmethod
    def crear_excepcion(psicologo_id, data):
        excepcion = ExcepcionDisponibilidad(
            psicologo_id=psicologo_id,
            fecha=data['fecha'],
            motivo=data.get('motivo')
        )
        db.session.add(excepcion)
        db.session.commit()
        return excepcion

    # ------------------------------------------------------------------
    # Generar slots para una fecha concreta
    # ------------------------------------------------------------------
    @staticmethod
    def obtener_slots_disponibles(psicologo_id, fecha_str):
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo

        # Fines de semana → sin horario
        if dia_semana > 4:
            return []

        # Verificar si hay excepción para ese día
        excepcion = ExcepcionDisponibilidad.query.filter_by(
            psicologo_id=psicologo_id, fecha=fecha
        ).first()
        if excepcion:
            return []  # No hay slots disponibles ese día

        # ---------------------------------------------------------------
        # Obtener bloques configurados en la BD
        # ---------------------------------------------------------------
        bloques = Disponibilidad.query.filter_by(
            psicologo_id=psicologo_id, dia_semana=dia_semana, activo=True
        ).all()

        # Si no hay bloques configurados → usar horario fijo por defecto
        if not bloques:
            bloques_data = [
                {"hora_inicio": HORARIO_FIJO_MANANA[0], "hora_fin": HORARIO_FIJO_MANANA[1], "duracion_slot": DURACION_SLOT_MINUTOS},
                {"hora_inicio": HORARIO_FIJO_TARDE[0], "hora_fin": HORARIO_FIJO_TARDE[1], "duracion_slot": DURACION_SLOT_MINUTOS},
            ]
        else:
            bloques_data = [
                {"hora_inicio": b.hora_inicio, "hora_fin": b.hora_fin, "duracion_slot": b.duracion_slot}
                for b in bloques
            ]

        # ---------------------------------------------------------------
        # Obtener citas existentes (PENDIENTES O CONFIRMADAS) para ese día
        # ---------------------------------------------------------------
        inicio_dia = datetime.combine(fecha, datetime.min.time())
        fin_dia = datetime.combine(fecha, datetime.max.time())

        citas_existentes = Cita.query.filter(
            Cita.psicologo_id == psicologo_id,
            Cita.estado.in_(['PENDIENTE', 'CONFIRMADA']),
            Cita.fecha_hora_inicio >= inicio_dia,
            Cita.fecha_hora_inicio <= fin_dia
        ).all()

        slots_ocupados = [
            (c.fecha_hora_inicio.time(), c.fecha_hora_fin.time())
            for c in citas_existentes
        ]

        # ---------------------------------------------------------------
        # Generar todos los slots y marcar disponibilidad
        # ---------------------------------------------------------------
        todos_los_slots = []
        for bloque in bloques_data:
            slots_teoricos = generar_slots(
                bloque["hora_inicio"], bloque["hora_fin"], bloque["duracion_slot"]
            )

            for slot in slots_teoricos:
                slot_inicio = datetime.strptime(slot['hora_inicio'], '%H:%M:%S').time()
                slot_fin = datetime.strptime(slot['hora_fin'], '%H:%M:%S').time()

                # Verificar solapamiento con citas existentes
                solapado = False
                for ocupado_inicio, ocupado_fin in slots_ocupados:
                    if slot_inicio < ocupado_fin and slot_fin > ocupado_inicio:
                        solapado = True
                        break

                # Verificar que el slot no sea en el pasado si es hoy
                slot_datetime = datetime.combine(fecha, slot_inicio)
                en_pasado = slot_datetime <= datetime.now()

                slot['disponible'] = not solapado and not en_pasado
                todos_los_slots.append(slot)

        return todos_los_slots
