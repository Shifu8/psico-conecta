from marshmallow import Schema, fields


class SesionSchema(Schema):
    id = fields.UUID(dump_only=True)
    cita_id = fields.UUID(dump_only=True)
    paciente_id = fields.Integer(dump_only=True)
    psicologo_id = fields.Integer(dump_only=True)
    tema = fields.String(dump_only=True)
    fecha_hora_inicio = fields.DateTime(dump_only=True)
    fecha_hora_fin = fields.DateTime(dump_only=True)
    estado = fields.String(dump_only=True)
    zoom_configurada = fields.Boolean(dump_only=True)
    puede_ingresar = fields.Boolean(dump_only=True)
    disponible_desde = fields.DateTime(dump_only=True, allow_none=True)
    mensaje_acceso = fields.String(dump_only=True, allow_none=True)


class AccesoSchema(Schema):
    cita_id = fields.UUID(dump_only=True)
    rol = fields.String(dump_only=True)
    url = fields.Url(dump_only=True)
    expira_en = fields.DateTime(dump_only=True, allow_none=True)
