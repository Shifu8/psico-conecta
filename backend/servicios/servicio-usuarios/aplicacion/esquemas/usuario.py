from marshmallow import Schema, fields, validate


class UserUpdateSchema(Schema):
    first_name = fields.String(validate=validate.Length(min=2, max=80))
    last_name = fields.String(validate=validate.Length(min=2, max=80))
    phone = fields.String(allow_none=True, validate=validate.Length(max=30))
    role = fields.String(validate=validate.OneOf(["ADMIN", "PSYCHOLOGIST", "PATIENT"]))


class UserStatusSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(["active", "inactive"]))

