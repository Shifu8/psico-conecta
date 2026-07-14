from datetime import datetime

from flask import Blueprint, g, jsonify, request

from app.esquemas.esquema_cita import (
    ActualizarNotasSchema,
    AgendarCitaSchema,
    CancelarCitaSchema,
    CitaSchema,
    ESTADOS,
    HistorialCambioCitaSchema,
    ReprogramarCitaSchema,
)
from app.modelos.cita import Cita
from app.servicios.servicio_cita import ServicioCita
from app.utilidades.autenticacion import requiere_rol
from app.utilidades.errores import ErrorDominio
from app.utilidades.tiempo import asegurar_datetime_utc


bp_citas = Blueprint("citas", __name__)
cita_schema = CitaSchema()
citas_schema = CitaSchema(many=True)
historial_schema = HistorialCambioCitaSchema(many=True)


def _json():
    return request.get_json(silent=True) or {}


@bp_citas.post("")
@requiere_rol("PACIENTE")
def agendar_cita():
    datos = AgendarCitaSchema().load(_json())
    cita = ServicioCita.agendar_cita(g.usuario_id, datos)
    return jsonify(cita_schema.dump(cita)), 201


@bp_citas.get("")
@requiere_rol("ADMIN")
def obtener_todas_las_citas():
    consulta = Cita.query
    estado = request.args.get("estado")
    if estado:
        estado = estado.upper()
        if estado not in ESTADOS:
            raise ErrorDominio("El filtro de estado no es válido.")
        consulta = consulta.filter(Cita.estado == estado)

    psicologo_id = request.args.get("psicologo_id", type=int)
    paciente_id = request.args.get("paciente_id", type=int)
    if psicologo_id:
        consulta = consulta.filter(Cita.psicologo_id == psicologo_id)
    if paciente_id:
        consulta = consulta.filter(Cita.paciente_id == paciente_id)

    for parametro, operador in (
        ("fecha_desde", lambda fecha: Cita.fecha_hora_inicio >= fecha),
        ("fecha_hasta", lambda fecha: Cita.fecha_hora_inicio <= fecha),
    ):
        valor = request.args.get(parametro)
        if valor:
            try:
                fecha = asegurar_datetime_utc(
                    datetime.fromisoformat(valor.replace("Z", "+00:00"))
                )
            except ValueError:
                raise ErrorDominio(f"El parámetro {parametro} no es una fecha válida.") from None
            consulta = consulta.filter(operador(fecha))

    citas = consulta.order_by(Cita.fecha_hora_inicio.desc()).all()
    return jsonify(citas_schema.dump(citas))


@bp_citas.get("/mis-citas")
@requiere_rol("PACIENTE", "PSICOLOGO")
def mis_citas():
    consulta = Cita.query
    if g.usuario_rol == "PACIENTE":
        consulta = consulta.filter(Cita.paciente_id == g.usuario_id)
    else:
        consulta = consulta.filter(Cita.psicologo_id == g.usuario_id)

    estado = request.args.get("estado")
    if estado:
        estado = estado.upper()
        if estado not in ESTADOS:
            raise ErrorDominio("El filtro de estado no es válido.")
        consulta = consulta.filter(Cita.estado == estado)

    citas = consulta.order_by(Cita.fecha_hora_inicio.desc()).all()
    return jsonify(citas_schema.dump(citas))


@bp_citas.get("/<uuid:cita_id>")
@requiere_rol("PACIENTE", "PSICOLOGO", "ADMIN")
def obtener_cita(cita_id):
    cita = ServicioCita.obtener(cita_id)
    ServicioCita.verificar_acceso(cita, g.usuario_id, g.usuario_rol)
    return jsonify(cita_schema.dump(cita))


@bp_citas.put("/<uuid:cita_id>/confirmar")
@requiere_rol("PSICOLOGO")
def confirmar_cita(cita_id):
    cita = ServicioCita.cambiar_estado(
        cita_id, "CONFIRMAR", g.usuario_id, g.usuario_rol
    )
    return jsonify(cita_schema.dump(cita))


@bp_citas.put("/<uuid:cita_id>/cancelar")
@requiere_rol("PACIENTE", "PSICOLOGO", "ADMIN")
def cancelar_cita(cita_id):
    datos = CancelarCitaSchema().load(_json())
    cita = ServicioCita.cambiar_estado(
        cita_id,
        "CANCELAR",
        g.usuario_id,
        g.usuario_rol,
        motivo=datos["motivo"],
    )
    return jsonify(cita_schema.dump(cita))


@bp_citas.put("/<uuid:cita_id>/reprogramar")
@requiere_rol("PACIENTE", "PSICOLOGO", "ADMIN")
def reprogramar_cita(cita_id):
    datos = ReprogramarCitaSchema().load(_json())
    cita = ServicioCita.reprogramar(
        cita_id,
        datos["nueva_fecha_hora_inicio"],
        g.usuario_id,
        g.usuario_rol,
    )
    return jsonify(cita_schema.dump(cita))


@bp_citas.put("/<uuid:cita_id>/completar")
@requiere_rol("PSICOLOGO")
def completar_cita(cita_id):
    cita = ServicioCita.cambiar_estado(
        cita_id, "COMPLETAR", g.usuario_id, g.usuario_rol
    )
    return jsonify(cita_schema.dump(cita))


@bp_citas.put("/<uuid:cita_id>/no-asistida")
@requiere_rol("PSICOLOGO")
def marcar_no_asistida(cita_id):
    cita = ServicioCita.cambiar_estado(
        cita_id, "NO_ASISTIDA", g.usuario_id, g.usuario_rol
    )
    return jsonify(cita_schema.dump(cita))


@bp_citas.put("/<uuid:cita_id>/notas")
@requiere_rol("PSICOLOGO")
def actualizar_notas(cita_id):
    datos = ActualizarNotasSchema().load(_json())
    cita = ServicioCita.actualizar_notas(
        cita_id, datos["notas"], g.usuario_id, g.usuario_rol
    )
    return jsonify(cita_schema.dump(cita))


@bp_citas.get("/<uuid:cita_id>/historial")
@requiere_rol("PACIENTE", "PSICOLOGO", "ADMIN")
def obtener_historial(cita_id):
    cita = ServicioCita.obtener(cita_id)
    ServicioCita.verificar_acceso(cita, g.usuario_id, g.usuario_rol)
    return jsonify(historial_schema.dump(ServicioCita.historial(cita_id)))
