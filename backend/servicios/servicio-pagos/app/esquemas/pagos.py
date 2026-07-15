from marshmallow import Schema, fields, validate


class ReembolsoSchema(Schema):
    monto_centavos = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1),
    )
    razon = fields.String(
        load_default="requested_by_customer",
        validate=validate.OneOf(["duplicate", "fraudulent", "requested_by_customer"]),
    )
    nota = fields.String(allow_none=True, validate=validate.Length(max=500))


class TarifaSchema(Schema):
    psicologo_id = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    modalidad = fields.String(
        load_default="TODAS",
        validate=validate.OneOf(["TODAS", "VIRTUAL", "PRESENCIAL"]),
    )
    monto_centavos = fields.Integer(required=True, validate=validate.Range(min=100, max=1000000))
    moneda = fields.String(load_default="USD", validate=validate.Length(equal=3))


class SincronizarCitaSchema(Schema):
    actor_id = fields.Integer(allow_none=True)
    cita = fields.Dict(required=True)
