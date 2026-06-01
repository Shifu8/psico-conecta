from marshmallow import Schema, fields, pre_load, validate

from aplicacion.utilidades.validacion import (
    normalize_spaces,
    validate_role_name,
)


class RoleSchema(Schema):
    name = fields.String(
        required=True,
        validate=[validate.Length(min=2, max=40), validate_role_name],
    )
    description = fields.String(load_default="", validate=validate.Length(max=255))
    permissions = fields.List(
        fields.String(validate=validate.Length(min=1, max=80)),
        load_default=list,
        validate=validate.Length(max=50),
    )

    @pre_load
    def normalize(self, data, **_kwargs):
        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        if "name" in normalized:
            normalized["name"] = normalize_spaces(normalized["name"])
        if "description" in normalized:
            normalized["description"] = normalize_spaces(normalized["description"])
        if isinstance(normalized.get("permissions"), list):
            normalized["permissions"] = [
                normalize_spaces(permission)
                for permission in normalized["permissions"]
            ]
        return normalized
