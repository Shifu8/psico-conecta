from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(min=2, max=80))
    last_name = fields.String(required=True, validate=validate.Length(min=2, max=80))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=8))
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    token = fields.String(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=8))

