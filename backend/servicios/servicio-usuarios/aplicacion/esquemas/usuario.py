# Archivo: usuario.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

from marshmallow import Schema, fields, pre_load, validate

from aplicacion.utilidades.validacion import (
    normalize_phone,
    normalize_spaces,
    validate_name,
    validate_phone,
)


class UserUpdateSchema(Schema):
    first_name = fields.String(validate=[validate.Length(min=2, max=80), validate_name])
    last_name = fields.String(validate=[validate.Length(min=2, max=80), validate_name])
    phone = fields.String(allow_none=True, validate=validate_phone)
    role = fields.String(validate=validate.OneOf(["ADMIN", "PSYCHOLOGIST", "PATIENT"]))

    @pre_load
    def normalize(self, data, **_kwargs):
        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        if "first_name" in normalized:
            normalized["first_name"] = normalize_spaces(normalized["first_name"])
        if "last_name" in normalized:
            normalized["last_name"] = normalize_spaces(normalized["last_name"])
        if "phone" in normalized:
            normalized["phone"] = normalize_phone(normalized["phone"])
        return normalized


class UserStatusSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(["active", "inactive"]))
