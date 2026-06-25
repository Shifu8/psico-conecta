# Archivo: esquema_disponibilidad.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Citas

from marshmallow import Schema, fields, validate, validates, ValidationError

class DisponibilidadSchema(Schema):
    id = fields.UUID(dump_only=True)
    psicologo_id = fields.UUID(dump_only=True)
    dia_semana = fields.Integer(required=True, validate=validate.Range(min=0, max=6))
    hora_inicio = fields.Time(required=True)
    hora_fin = fields.Time(required=True)
    duracion_slot = fields.Integer(load_default=50, validate=validate.Range(min=15, max=120))
    activo = fields.Boolean(load_default=True)
    
    @validates('hora_fin')
    def validar_horas(self, value, **kwargs):
        # Para validar hora_inicio < hora_fin necesitamos validar a nivel de objeto
        pass

class CrearDisponibilidadSchema(Schema):
    dia_semana = fields.Integer(required=True, validate=validate.Range(min=0, max=6))
    hora_inicio = fields.Time(required=True)
    hora_fin = fields.Time(required=True)
    duracion_slot = fields.Integer(load_default=50, validate=validate.Range(min=15, max=120))

class ExcepcionDisponibilidadSchema(Schema):
    id = fields.UUID(dump_only=True)
    psicologo_id = fields.UUID(dump_only=True)
    fecha = fields.Date(required=True)
    motivo = fields.String(validate=validate.Length(max=255), allow_none=True)

class CrearExcepcionSchema(Schema):
    fecha = fields.Date(required=True)
    motivo = fields.String(validate=validate.Length(max=255), allow_none=True)
