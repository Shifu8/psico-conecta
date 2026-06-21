from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from app.utilidades.autenticacion import requiere_rol, _extraer_rol
from app.servicios.servicio_cita import ServicioCita
from app.modelos.cita import Cita
from app.esquemas.esquema_cita import CitaSchema, AgendarCitaSchema, CancelarCitaSchema
from app.utilidades.helpers import parse_iso_datetime

bp_citas = Blueprint('citas', __name__)
cita_schema = CitaSchema()
citas_list_schema = CitaSchema(many=True)

@bp_citas.route('', methods=['POST'])
@requiere_rol('PACIENTE')
def agendar_cita():
    claims = get_jwt()
    paciente_id = claims.get('sub')
    
    schema = AgendarCitaSchema()
    data = request.json
    
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
        
    # Pre-parse date for logic
    if 'fecha_hora_inicio' in data:
        dt = parse_iso_datetime(data['fecha_hora_inicio'])
        if dt:
            data['fecha_hora_inicio'] = dt
        
    cita, error = ServicioCita.agendar_cita(paciente_id, data)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify(cita_schema.dump(cita)), 201

@bp_citas.route('/mis-citas', methods=['GET'])
@requiere_rol('PACIENTE', 'PSICOLOGO')
def mis_citas():
    claims = get_jwt()
    user_id = claims.get('sub')
    rol = _extraer_rol(claims)
    
    if rol == 'PACIENTE':
        citas = Cita.query.filter_by(paciente_id=user_id).order_by(Cita.fecha_hora_inicio.desc()).all()
    else:
        citas = Cita.query.filter_by(psicologo_id=user_id).order_by(Cita.fecha_hora_inicio.desc()).all()
        
    return jsonify(citas_list_schema.dump(citas)), 200

@bp_citas.route('/<uuid:cita_id>', methods=['GET'])
@requiere_rol('PACIENTE', 'PSICOLOGO', 'ADMIN')
def obtener_cita(cita_id):
    claims = get_jwt()
    user_id = claims.get('sub')
    rol = _extraer_rol(claims)
    
    cita = Cita.query.get(cita_id)
    if not cita:
        return jsonify({"error": "Cita no encontrada"}), 404
        
    if rol == 'PACIENTE' and cita.paciente_id != user_id:
        return jsonify({"error": "No tienes acceso a esta cita"}), 403
    if rol == 'PSICOLOGO' and cita.psicologo_id != user_id:
        return jsonify({"error": "No tienes acceso a esta cita"}), 403
        
    return jsonify(cita_schema.dump(cita)), 200

@bp_citas.route('/<uuid:cita_id>/confirmar', methods=['PUT'])
@requiere_rol('PSICOLOGO')
def confirmar_cita(cita_id):
    claims = get_jwt()
    user_id = claims.get('sub')
    
    cita, error = ServicioCita.cambiar_estado(cita_id, 'CONFIRMADA', user_id, 'PSICOLOGO')
    if error:
        return jsonify({"error": error}), 400
    return jsonify(cita_schema.dump(cita)), 200

@bp_citas.route('/<uuid:cita_id>/cancelar', methods=['PUT'])
@requiere_rol('PACIENTE', 'PSICOLOGO', 'ADMIN')
def cancelar_cita(cita_id):
    claims = get_jwt()
    user_id = claims.get('sub')
    rol = _extraer_rol(claims)
    
    schema = CancelarCitaSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify(errors), 400
        
    motivo = request.json.get('motivo')
    
    cita, error = ServicioCita.cambiar_estado(cita_id, 'CANCELADA', user_id, rol, motivo)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(cita_schema.dump(cita)), 200
