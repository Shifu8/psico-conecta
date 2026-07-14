from flask import Blueprint, g, jsonify

from app.esquemas import AccesoSchema, SesionSchema
from app.modelos import SesionZoom
from app.servicios.cliente_citas import ClienteCitas
from app.servicios.servicio_teleconsulta import ServicioTeleconsulta
from app.utilidades.autenticacion import requiere_rol, requiere_token_interno
from app.utilidades.errores import ErrorDominio

bp = Blueprint("teleconsultas", __name__)
sesion_schema = SesionSchema()
sesiones_schema = SesionSchema(many=True)
acceso_schema = AccesoSchema()


@bp.get("/mis-sesiones")
@requiere_rol("PACIENTE", "PSICOLOGO")
def mis_sesiones():
    citas = ClienteCitas.mis_citas()
    for cita in citas:
        if str(cita.get("modalidad", "")).upper() == "VIRTUAL":
            try:
                ServicioTeleconsulta.sincronizar_desde_cita(cita, g.usuario_id)
            except ErrorDominio:
                # El listado sigue disponible y muestra el estado de error persistido.
                pass
    filtro = (
        SesionZoom.paciente_id == g.usuario_id
        if g.usuario_rol == "PACIENTE"
        else SesionZoom.psicologo_id == g.usuario_id
    )
    sesiones = SesionZoom.query.filter(filtro).order_by(SesionZoom.fecha_hora_inicio.asc()).all()
    datos = [ServicioTeleconsulta.serializar(s, g.usuario_rol) for s in sesiones]
    return jsonify(sesiones_schema.dump(datos))


@bp.get("/cita/<uuid:cita_id>")
@requiere_rol("PACIENTE", "PSICOLOGO", "ADMIN")
def obtener_por_cita(cita_id):
    cita = ClienteCitas.obtener_cita(cita_id)
    ServicioTeleconsulta.verificar_propiedad(cita, g.usuario_id, g.usuario_rol)
    sesion = ServicioTeleconsulta.sincronizar_desde_cita(cita, g.usuario_id)
    if not sesion:
        raise ErrorDominio(
            "La cita debe ser virtual y estar confirmada para generar una teleconsulta.",
            409,
            "cita_no_elegible",
        )
    return jsonify(sesion_schema.dump(ServicioTeleconsulta.serializar(sesion, g.usuario_rol)))


@bp.post("/cita/<uuid:cita_id>/acceso")
@requiere_rol("PACIENTE", "PSICOLOGO")
def acceso(cita_id):
    cita = ClienteCitas.obtener_cita(cita_id)
    ServicioTeleconsulta.verificar_propiedad(cita, g.usuario_id, g.usuario_rol)
    sesion = ServicioTeleconsulta.sincronizar_desde_cita(cita, g.usuario_id)
    if not sesion:
        raise ErrorDominio("La cita no tiene una teleconsulta activa.", 409, "cita_no_elegible")
    return jsonify(acceso_schema.dump(ServicioTeleconsulta.obtener_acceso(sesion, g.usuario_rol)))


@bp.post("/interna/citas/sincronizar")
@requiere_token_interno
def sincronizar_interna():
    from flask import request

    payload = request.get_json(silent=True) or {}
    cita = payload.get("cita") or payload
    sesion = ServicioTeleconsulta.sincronizar_desde_cita(cita, payload.get("actor_id"))
    if not sesion:
        return jsonify(sesion=None, mensaje="La cita no requiere teleconsulta."), 200
    return jsonify(sesion=sesion_schema.dump(ServicioTeleconsulta.serializar(sesion, "ADMIN"))), 200
