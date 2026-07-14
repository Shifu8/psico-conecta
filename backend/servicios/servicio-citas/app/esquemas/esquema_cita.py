from marshmallow import Schema, fields, validate


ESTADOS = [
    "PENDIENTE", "CONFIRMADA", "REPROGRAMADA", "CANCELADA",
    "COMPLETADA", "NO_ASISTIDA",
]
MODALIDADES = ["VIRTUAL", "PRESENCIAL"]


class CitaSchema(Schema):
    id = fields.UUID(dump_only=True)
    paciente_id = fields.Integer(dump_only=True)
    psicologo_id = fields.Integer(dump_only=True)
    fecha_hora_inicio = fields.DateTime(dump_only=True)
    fecha_hora_fin = fields.DateTime(dump_only=True)
    estado = fields.String(dump_only=True)
    modalidad = fields.String(dump_only=True)
    motivo_consulta = fields.String(dump_only=True, allow_none=True)
    notas_psicologo = fields.String(dump_only=True, allow_none=True)
    motivo_cancelacion = fields.String(dump_only=True, allow_none=True)
    cancelado_por = fields.Integer(dump_only=True, allow_none=True)
    reprogramada_desde = fields.UUID(dump_only=True, allow_none=True)
    fecha_creacion = fields.DateTime(dump_only=True)
    fecha_actualizacion = fields.DateTime(dump_only=True)


class AgendarCitaSchema(Schema):
    psicologo_id = fields.Integer(required=True, validate=validate.Range(min=1))
    fecha_hora_inicio = fields.DateTime(required=True)
    modalidad = fields.String(
        load_default="VIRTUAL", validate=validate.OneOf(MODALIDADES)
    )
    motivo_consulta = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=500)
    )


class ReprogramarCitaSchema(Schema):
    nueva_fecha_hora_inicio = fields.DateTime(required=True)


class CancelarCitaSchema(Schema):
    motivo = fields.String(required=True, validate=validate.Length(min=5, max=255))


class ActualizarNotasSchema(Schema):
    notas = fields.String(required=True, validate=validate.Length(max=5000))


class HistorialCambioCitaSchema(Schema):
    id = fields.UUID(dump_only=True)
    cita_id = fields.UUID(dump_only=True)
    accion = fields.String(dump_only=True)
    estado_anterior = fields.String(dump_only=True, allow_none=True)
    estado_nuevo = fields.String(dump_only=True)
    cambiado_por = fields.Integer(dump_only=True)
    motivo = fields.String(dump_only=True, allow_none=True)
    datos_anteriores = fields.Dict(dump_only=True, allow_none=True)
    datos_nuevos = fields.Dict(dump_only=True, allow_none=True)
    fecha_cambio = fields.DateTime(dump_only=True)
