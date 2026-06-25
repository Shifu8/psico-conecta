# Archivo: servicio_cita.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Citas

from app import db
from app.modelos.cita import Cita
from app.modelos.historial import HistorialCambioCita
from app.modelos.disponibilidad import Disponibilidad
from datetime import datetime, timedelta
import pytz

DURACION_CITA_MINUTOS = 60


class ServicioCita:
    @staticmethod
    def agendar_cita(paciente_id, data):
        fecha_inicio = data['fecha_hora_inicio']
        duracion = DURACION_CITA_MINUTOS
        
        # Validar solapamiento de cita
        solapada = Cita.query.filter(
            Cita.psicologo_id == data['psicologo_id'],
            Cita.estado.in_(['PENDIENTE', 'CONFIRMADA']),
            Cita.fecha_hora_inicio < fecha_inicio + timedelta(minutes=duracion),
            Cita.fecha_hora_fin > fecha_inicio
        ).first()
        
        if solapada:
            return None, "El horario seleccionado ya no está disponible."
            
        nueva_cita = Cita(
            paciente_id=paciente_id,
            psicologo_id=data['psicologo_id'],
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_inicio + timedelta(minutes=duracion),
            modalidad=data.get('modalidad', 'VIRTUAL'),
            motivo_consulta=data.get('motivo_consulta')
        )
        
        db.session.add(nueva_cita)
        db.session.flush() # Para obtener el ID
        
        ServicioCita.registrar_historial(nueva_cita.id, None, 'PENDIENTE', paciente_id, "Creación de cita")
        
        db.session.commit()
        return nueva_cita, None

    @staticmethod
    def cambiar_estado(cita_id, nuevo_estado, solicitante_id, rol_solicitante, motivo=None):
        cita = Cita.query.get(cita_id)
        if not cita:
            return None, "Cita no encontrada."
            
        # Validar permisos
        if rol_solicitante == 'PACIENTE' and cita.paciente_id != solicitante_id:
            return None, "No tienes permiso sobre esta cita."
        if rol_solicitante == 'PSICOLOGO' and cita.psicologo_id != solicitante_id:
            return None, "No tienes permiso sobre esta cita."
            
        # Lógica específica de estados
        estado_anterior = cita.estado
        if nuevo_estado == 'CANCELADA':
            if cita.estado in ['COMPLETADA', 'CANCELADA']:
                return None, "No se puede cancelar una cita completada o ya cancelada."
            cita.cancelado_por = solicitante_id
            cita.motivo_cancelacion = motivo
            
        cita.estado = nuevo_estado
        ServicioCita.registrar_historial(cita.id, estado_anterior, nuevo_estado, solicitante_id, motivo)
        db.session.commit()
        return cita, None
        
    @staticmethod
    def registrar_historial(cita_id, estado_anterior, estado_nuevo, cambiado_por, motivo):
        historial = HistorialCambioCita(
            cita_id=cita_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            cambiado_por=cambiado_por,
            motivo=motivo
        )
        db.session.add(historial)
