from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
import pytz

class CitaSchema(Schema):
    id = fields.UUID(dump_only=True)
    paciente_id = fields.UUID(required=True)
    psicologo_id = fields.UUID(required=True)
    fecha_hora_inicio = fields.DateTime(required=True)
    fecha_hora_fin = fields.DateTime(required=True)
    estado = fields.String(validate=validate.OneOf(['PENDIENTE', 'CONFIRMADA', 'REPROGRAMADA', 'CANCELADA', 'COMPLETADA', 'NO_ASISTIDA']))
    modalidad = fields.String(validate=validate.OneOf(['VIRTUAL', 'PRESENCIAL']))
    motivo_consulta = fields.String(validate=validate.Length(max=500), allow_none=True)
    notas_psicologo = fields.String(allow_none=True)
    motivo_cancelacion = fields.String(allow_none=True)
    cancelado_por = fields.UUID(allow_none=True)
    reprogramada_desde = fields.UUID(allow_none=True)
    fecha_creacion = fields.DateTime(dump_only=True)
    fecha_actualizacion = fields.DateTime(dump_only=True)

class AgendarCitaSchema(Schema):
    psicologo_id = fields.UUID(required=True)
    fecha_hora_inicio = fields.DateTime(required=True)
    modalidad = fields.String(validate=validate.OneOf(['VIRTUAL', 'PRESENCIAL']), load_default='VIRTUAL')
    motivo_consulta = fields.String(validate=validate.Length(max=500), allow_none=True)

    @validates('fecha_hora_inicio')
    def no_en_el_pasado(self, value):
        if value.replace(tzinfo=pytz.UTC) < datetime.utcnow().replace(tzinfo=pytz.UTC):
            raise ValidationError('No se pueden agendar citas en el pasado.')

class ReprogramarCitaSchema(Schema):
    nueva_fecha_hora_inicio = fields.DateTime(required=True)

    @validates('nueva_fecha_hora_inicio')
    def no_en_el_pasado(self, value):
        if value.replace(tzinfo=pytz.UTC) < datetime.utcnow().replace(tzinfo=pytz.UTC):
            raise ValidationError('No se pueden reprogramar citas en el pasado.')

class CancelarCitaSchema(Schema):
    motivo = fields.String(required=True, validate=validate.Length(min=5, max=255))

class HistorialCambioCitaSchema(Schema):
    id = fields.UUID(dump_only=True)
    cita_id = fields.UUID(required=True)
    estado_anterior = fields.String(allow_none=True)
    estado_nuevo = fields.String(required=True)
    cambiado_por = fields.UUID(required=True)
    motivo = fields.String(allow_none=True)
    fecha_cambio = fields.DateTime(dump_only=True)
