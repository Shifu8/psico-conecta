from flask import Blueprint, g, jsonify, request

from app.esquemas import ReembolsoSchema, SincronizarCitaSchema, TarifaSchema
from app.servicios.cliente_citas import ClienteCitas
from app.servicios.servicio_pagos import ServicioPagos
from app.utilidades.autenticacion import requiere_rol, requiere_token_interno
from app.utilidades.errores import ErrorDominio


bp = Blueprint("pagos", __name__)


@bp.get("/mis-pagos")
@requiere_rol("PACIENTE", "PSICOLOGO", "ADMIN")
def mis_pagos():
    pagos = ServicioPagos.listar(
        g.usuario_id,
        g.usuario_rol,
        estado=request.args.get("estado"),
    )
    return jsonify([
        ServicioPagos.serializar(pago, g.usuario_rol)
        for pago in pagos
    ])


@bp.get("")
@bp.get("/")
@requiere_rol("ADMIN")
def listar_todos():
    pagos = ServicioPagos.listar(
        g.usuario_id,
        g.usuario_rol,
        estado=request.args.get("estado"),
    )
    return jsonify(pagos=[ServicioPagos.serializar(pago, "ADMIN") for pago in pagos])


@bp.get("/<pago_id>")
@requiere_rol("PACIENTE", "PSICOLOGO", "ADMIN")
def detalle_pago(pago_id):
    pago = ServicioPagos._obtener_pago(pago_id)
    ServicioPagos._verificar_acceso(pago, g.usuario_id, g.usuario_rol)
    return jsonify(pago=ServicioPagos.serializar(pago, g.usuario_rol, incluir_historial=True))


@bp.get("/cita/<cita_id>")
@requiere_rol("PACIENTE", "PSICOLOGO", "ADMIN")
def pago_por_cita(cita_id):
    pago = ServicioPagos.obtener_por_cita(cita_id)
    if not pago:
        # El servicio de citas valida que el usuario tenga acceso al expediente solicitado.
        ClienteCitas.obtener_cita(cita_id)
        return jsonify(pago=None)
    ServicioPagos._verificar_acceso(pago, g.usuario_id, g.usuario_rol)
    return jsonify(pago=ServicioPagos.serializar(pago, g.usuario_rol, incluir_historial=True))


@bp.post("/cita/<cita_id>/checkout")
@requiere_rol("PACIENTE")
def crear_checkout(cita_id):
    pago = ServicioPagos.obtener_por_cita(cita_id)
    if not pago:
        cita = ClienteCitas.obtener_cita(cita_id)
        if int(cita.get("paciente_id", -1)) != int(g.usuario_id):
            raise ErrorDominio("No tienes acceso a esta cita.", 403, "acceso_denegado")
        if str(cita.get("estado", "")).upper() != "CONFIRMADA":
            raise ErrorDominio(
                "La cita debe estar confirmada antes de iniciar el pago.",
                409,
                "cita_no_confirmada",
            )
        pago = ServicioPagos.sincronizar_desde_cita(cita, g.usuario_id)
    if not pago:
        raise ErrorDominio(
            "No fue posible preparar el pago de la cita.",
            409,
            "pago_no_preparado",
        )
    email = (g.usuario_perfil or {}).get("email")
    pago = ServicioPagos.crear_checkout(pago, g.usuario_id, email=email)
    return jsonify(pago=ServicioPagos.serializar(pago, "PACIENTE"))


@bp.post("/checkout/<session_id>/sincronizar")
@requiere_rol("PACIENTE", "ADMIN")
def sincronizar_checkout(session_id):
    pago = ServicioPagos.sincronizar_checkout(
        session_id,
        g.usuario_id,
        g.usuario_rol,
    )
    return jsonify(pago=ServicioPagos.serializar(pago, g.usuario_rol, incluir_historial=True))


@bp.post("/<pago_id>/reembolsar")
@requiere_rol("ADMIN")
def reembolsar(pago_id):
    datos = ReembolsoSchema().load(request.get_json(silent=True) or {})
    pago = ServicioPagos.crear_reembolso(
        pago_id,
        solicitado_por=g.usuario_id,
        monto_centavos=datos.get("monto_centavos"),
        razon=datos.get("razon", "requested_by_customer"),
        nota=datos.get("nota"),
    )
    return jsonify(pago=ServicioPagos.serializar(pago, "ADMIN", incluir_historial=True))


@bp.post("/sincronizar-citas")
@requiere_rol("ADMIN")
def sincronizar_citas_existentes():
    citas = ClienteCitas.listar_citas(estado="CONFIRMADA")
    resultado = ServicioPagos.sincronizar_citas_existentes(citas, g.usuario_id)
    codigo = 207 if resultado["errores"] else 200
    return jsonify(resultado), codigo


@bp.get("/tarifas")
@requiere_rol("ADMIN")
def listar_tarifas():
    solo_activas = request.args.get("activas", "false").lower() in {"1", "true", "si", "sí"}
    return jsonify(
        tarifas=[
            ServicioPagos.serializar_tarifa(tarifa)
            for tarifa in ServicioPagos.listar_tarifas(solo_activas)
        ]
    )


@bp.post("/tarifas")
@requiere_rol("ADMIN")
def crear_tarifa():
    datos = TarifaSchema().load(request.get_json(silent=True) or {})
    tarifa = ServicioPagos.crear_tarifa(datos, g.usuario_id)
    return jsonify(tarifa=ServicioPagos.serializar_tarifa(tarifa)), 201


@bp.delete("/tarifas/<tarifa_id>")
@requiere_rol("ADMIN")
def desactivar_tarifa(tarifa_id):
    tarifa = ServicioPagos.desactivar_tarifa(tarifa_id)
    return jsonify(tarifa=ServicioPagos.serializar_tarifa(tarifa))


@bp.post("/interna/citas/sincronizar")
@requiere_token_interno
def sincronizar_cita_interna():
    datos = SincronizarCitaSchema().load(request.get_json(silent=True) or {})
    pago = ServicioPagos.sincronizar_desde_cita(datos["cita"], datos.get("actor_id"))
    return jsonify(
        sincronizado=True,
        pago=ServicioPagos.serializar(pago, "ADMIN") if pago else None,
    )


@bp.get("/interna/citas/<cita_id>/estado")
@requiere_token_interno
def estado_pago_interno(cita_id):
    return jsonify(ServicioPagos.estado_interno_por_cita(cita_id))
