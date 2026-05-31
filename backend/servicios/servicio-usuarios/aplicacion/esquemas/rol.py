from marshmallow import Schema, fields, validate


class RoleSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=40))
    description = fields.String(load_default="", validate=validate.Length(max=255))
    permissions = fields.List(fields.String(), load_default=list)

