from marshmallow import Schema, fields, pre_load, validate

from aplicacion.utilidades.validacion import (
    normalize_email,
    normalize_phone,
    normalize_spaces,
    validate_name,
    validate_password,
    validate_phone,
)


class AuthenticationSchema(Schema):
    @pre_load
    def normalize(self, data, **_kwargs):
        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        if "email" in normalized:
            normalized["email"] = normalize_email(normalized["email"])
        if "first_name" in normalized:
            normalized["first_name"] = normalize_spaces(normalized["first_name"])
        if "last_name" in normalized:
            normalized["last_name"] = normalize_spaces(normalized["last_name"])
        if "phone" in normalized:
            normalized["phone"] = normalize_phone(normalized["phone"])
        if "token" in normalized:
            normalized["token"] = normalize_spaces(normalized["token"])
        return normalized


class RegisterSchema(AuthenticationSchema):
    first_name = fields.String(
        required=True, validate=[validate.Length(min=2, max=80), validate_name]
    )
    last_name = fields.String(
        required=True, validate=[validate.Length(min=2, max=80), validate_name]
    )
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.String(required=True, load_only=True, validate=validate_password)
    phone = fields.String(load_default=None, allow_none=True, validate=validate_phone)
    captcha_token = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=2048),
    )


class LoginSchema(AuthenticationSchema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.String(
        required=True, load_only=True, validate=validate.Length(min=1, max=15)
    )
    captcha_token = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=2048),
    )


class ForgotPasswordSchema(AuthenticationSchema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    captcha_token = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=2048),
    )


class ResetPasswordSchema(AuthenticationSchema):
    token = fields.String(required=True, validate=validate.Length(min=1, max=256))
    password = fields.String(required=True, load_only=True, validate=validate_password)


class GoogleLoginSchema(Schema):
    credential = fields.String(
        required=True,
        validate=validate.Length(min=1, max=5000),
    )
