from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class DisponibilidadSchema(Schema):
    id = fields.UUID(dump_only=True)
    psicologo_id = fields.Integer(dump_only=True)
    dia_semana = fields.Integer(dump_only=True)
    hora_inicio = fields.Time(dump_only=True)
    hora_fin = fields.Time(dump_only=True)
    duracion_slot = fields.Integer(dump_only=True)
    activo = fields.Boolean(dump_only=True)
    fecha_creacion = fields.DateTime(dump_only=True)
    fecha_actualizacion = fields.DateTime(dump_only=True)


class CrearDisponibilidadSchema(Schema):
    dia_semana = fields.Integer(required=True, strict=True, validate=validate.Range(min=0, max=6))
    hora_inicio = fields.Time(required=True)
    hora_fin = fields.Time(required=True)
    duracion_slot = fields.Integer(
        load_default=50, strict=True, validate=validate.Range(min=15, max=180)
    )

    @validates_schema
    def validar_rango(self, datos, **kwargs):
        if datos.get("hora_inicio") and datos.get("hora_fin"):
            if datos["hora_fin"] <= datos["hora_inicio"]:
                raise ValidationError(
                    {"hora_fin": ["La hora final debe ser posterior a la hora inicial."]}
                )


class ActualizarDisponibilidadSchema(Schema):
    dia_semana = fields.Integer(strict=True, validate=validate.Range(min=0, max=6))
    hora_inicio = fields.Time()
    hora_fin = fields.Time()
    duracion_slot = fields.Integer(strict=True, validate=validate.Range(min=15, max=180))
    activo = fields.Boolean()


class ExcepcionDisponibilidadSchema(Schema):
    id = fields.UUID(dump_only=True)
    psicologo_id = fields.Integer(dump_only=True)
    fecha = fields.Date(dump_only=True)
    motivo = fields.String(dump_only=True, allow_none=True)
    fecha_creacion = fields.DateTime(dump_only=True)


class CrearExcepcionSchema(Schema):
    fecha = fields.Date(required=True)
    motivo = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=255)
    )
