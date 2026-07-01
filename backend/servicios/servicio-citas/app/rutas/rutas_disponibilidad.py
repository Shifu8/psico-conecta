# Archivo: rutas_disponibilidad.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Citas

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from app.utilidades.autenticacion import requiere_rol
from app.servicios.servicio_disponibilidad import ServicioDisponibilidad
from app.esquemas.esquema_disponibilidad import DisponibilidadSchema, CrearDisponibilidadSchema, ExcepcionDisponibilidadSchema, CrearExcepcionSchema

bp_disponibilidad = Blueprint('disponibilidad', __name__)
disp_schema = DisponibilidadSchema()
disp_list_schema = DisponibilidadSchema(many=True)
excepcion_schema = ExcepcionDisponibilidadSchema()
excepcion_list_schema = ExcepcionDisponibilidadSchema(many=True)

@bp_disponibilidad.route('/<psicologo_id>', methods=['GET'])
def obtener_disponibilidad(psicologo_id):
    bloques = ServicioDisponibilidad.obtener_disponibilidad(psicologo_id)
    return jsonify(disp_list_schema.dump(bloques)), 200

@bp_disponibilidad.route('', methods=['POST'])
@requiere_rol('PSICOLOGO')
def crear_bloque():
    claims = get_jwt()
    psicologo_id = claims.get('sub') # id del usuario
    
    schema = CrearDisponibilidadSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify(errors), 400
        
    bloque = ServicioDisponibilidad.crear_bloque(psicologo_id, request.json)
    return jsonify(disp_schema.dump(bloque)), 201

@bp_disponibilidad.route('/<psicologo_id>/slots', methods=['GET'])
def obtener_slots(psicologo_id):
    fecha_str = request.args.get('fecha')
    if not fecha_str:
        return jsonify({"error": "Debe proporcionar el parámetro fecha (YYYY-MM-DD)"}), 400
        
    try:
        slots = ServicioDisponibilidad.obtener_slots_disponibles(psicologo_id, fecha_str)
        return jsonify({"fecha": fecha_str, "slots": slots}), 200
    except ValueError as e:
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400

@bp_disponibilidad.route('/<psicologo_id>/excepciones', methods=['GET'])
@requiere_rol('ADMIN')
def obtener_excepciones(psicologo_id):
    excepciones = ServicioDisponibilidad.obtener_excepciones(psicologo_id)
    return jsonify(excepcion_list_schema.dump(excepciones)), 200

@bp_disponibilidad.route('/<psicologo_id>/excepciones', methods=['POST'])
@requiere_rol('ADMIN')
def crear_excepcion(psicologo_id):
    schema = CrearExcepcionSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify(errors), 400
        
    excepcion = ServicioDisponibilidad.crear_excepcion(psicologo_id, request.json)
    return jsonify(excepcion_schema.dump(excepcion)), 201

@bp_disponibilidad.route('/excepciones/<excepcion_id>', methods=['DELETE'])
@requiere_rol('ADMIN')
def eliminar_excepcion(excepcion_id):
    if ServicioDisponibilidad.eliminar_excepcion(excepcion_id):
        return jsonify({"mensaje": "Excepción eliminada correctamente"}), 200
    return jsonify({"error": "Excepción no encontrada"}), 404
