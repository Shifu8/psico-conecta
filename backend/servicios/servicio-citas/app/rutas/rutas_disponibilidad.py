from flask import Blueprint, g, jsonify, request

from app.esquemas.esquema_disponibilidad import (
    ActualizarDisponibilidadSchema,
    CrearDisponibilidadSchema,
    CrearExcepcionSchema,
    DisponibilidadSchema,
    ExcepcionDisponibilidadSchema,
)
from app.servicios.servicio_disponibilidad import ServicioDisponibilidad
from app.utilidades.autenticacion import requiere_rol
from app.utilidades.errores import ErrorDominio


bp_disponibilidad = Blueprint("disponibilidad", __name__)
disponibilidad_schema = DisponibilidadSchema()
disponibilidades_schema = DisponibilidadSchema(many=True)
excepcion_schema = ExcepcionDisponibilidadSchema()
excepciones_schema = ExcepcionDisponibilidadSchema(many=True)


def _json():
    return request.get_json(silent=True) or {}


def _autorizar_administrador():
    if g.usuario_rol != "ADMIN":
        raise ErrorDominio(
            "Solo un administrador puede gestionar fechas no disponibles.",
            403,
            "acceso_denegado",
        )


@bp_disponibilidad.get("/<int:psicologo_id>")
def obtener_disponibilidad(psicologo_id):
    bloques = ServicioDisponibilidad.obtener_disponibilidad(psicologo_id)
    return jsonify(disponibilidades_schema.dump(bloques))


@bp_disponibilidad.post("")
@requiere_rol("ADMIN")
def crear_bloque():
    datos = CrearDisponibilidadSchema().load(_json())
    psicologo_id = request.args.get("psicologo_id", type=int)
    if not psicologo_id:
        raise ErrorDominio("Debes indicar psicologo_id para crear un bloque técnico.")
    bloque = ServicioDisponibilidad.crear_bloque(psicologo_id, datos)
    return jsonify(disponibilidad_schema.dump(bloque)), 201


@bp_disponibilidad.put("/<uuid:bloque_id>")
@requiere_rol("ADMIN")
def actualizar_bloque(bloque_id):
    from app.modelos.disponibilidad import Disponibilidad

    datos = ActualizarDisponibilidadSchema().load(_json())
    bloque_existente = Disponibilidad.query.filter_by(id=bloque_id).first()
    if not bloque_existente:
        raise ErrorDominio("Bloque de disponibilidad no encontrado.", 404, "no_encontrado")
    _autorizar_administrador()
    bloque = ServicioDisponibilidad.actualizar_bloque(
        bloque_id, bloque_existente.psicologo_id, datos
    )
    return jsonify(disponibilidad_schema.dump(bloque))


@bp_disponibilidad.delete("/<uuid:bloque_id>")
@requiere_rol("ADMIN")
def eliminar_bloque(bloque_id):
    from app.modelos.disponibilidad import Disponibilidad

    bloque = Disponibilidad.query.filter_by(id=bloque_id).first()
    if not bloque:
        raise ErrorDominio("Bloque de disponibilidad no encontrado.", 404, "no_encontrado")
    _autorizar_administrador()
    ServicioDisponibilidad.eliminar_bloque(bloque_id, bloque.psicologo_id)
    return jsonify(mensaje="Bloque eliminado correctamente.")


@bp_disponibilidad.get("/<int:psicologo_id>/slots")
def obtener_slots(psicologo_id):
    fecha = request.args.get("fecha")
    if not fecha:
        raise ErrorDominio("Debes proporcionar la fecha en formato YYYY-MM-DD.")
    slots = ServicioDisponibilidad.obtener_slots_disponibles(psicologo_id, fecha)
    return jsonify(fecha=fecha, psicologo_id=psicologo_id, slots=slots)


@bp_disponibilidad.get("/<int:psicologo_id>/excepciones")
@requiere_rol("ADMIN")
def obtener_excepciones(psicologo_id):
    _autorizar_administrador()
    excepciones = ServicioDisponibilidad.obtener_excepciones(psicologo_id)
    return jsonify(excepciones_schema.dump(excepciones))


@bp_disponibilidad.post("/<int:psicologo_id>/excepciones")
@requiere_rol("ADMIN")
def crear_excepcion(psicologo_id):
    _autorizar_administrador()
    datos = CrearExcepcionSchema().load(_json())
    excepcion = ServicioDisponibilidad.crear_excepcion(psicologo_id, datos)
    return jsonify(excepcion_schema.dump(excepcion)), 201


@bp_disponibilidad.delete("/excepciones/<uuid:excepcion_id>")
@requiere_rol("ADMIN")
def eliminar_excepcion(excepcion_id):
    excepcion = ServicioDisponibilidad.obtener_excepcion(excepcion_id)
    _autorizar_administrador()
    ServicioDisponibilidad.eliminar_excepcion(excepcion_id)
    return jsonify(mensaje="Excepción eliminada correctamente.")
