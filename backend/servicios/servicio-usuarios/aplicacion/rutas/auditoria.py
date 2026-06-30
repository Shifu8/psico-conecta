# Archivo: auditoria.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from aplicacion.intermediarios.roles import role_required
from aplicacion.modelos import AuditEvent
from aplicacion.servicios.servicio_auditoria import construir_resumen_auditoria, registrar_evento_auditoria

audit_bp = Blueprint("auditoria", __name__, url_prefix="/api/usuarios/auditoria")


@audit_bp.post("/registrar")
@jwt_required(optional=True)
def registrar_evento_ruta():
    data = request.get_json(silent=True) or {}
    
    # Intentar resolver identidad desde el token JWT si no viene explícita
    actor_email = data.get("actor_email")
    rol = data.get("rol")
    if not actor_email:
        identidad = get_jwt_identity()
        if isinstance(identidad, dict):
            actor_email = identidad.get("email")
            rol = identidad.get("role")
            
    registrar_evento_auditoria(
        event_type=data.get("event_type", "api_request"),
        category=data.get("category", "usuarios"),
        status=data.get("status", "success"),
        actor_email=actor_email,
        rol=rol,
        request_obj=request,
        modulo=data.get("modulo"),
        descripcion=data.get("descripcion"),
        severidad=data.get("severidad"),
        canal=data.get("canal", "Web"),
        accion=data.get("accion"),
    )
    return jsonify(message="Evento registrado correctamente."), 201


@audit_bp.get("/resumen")
@role_required("ADMIN")
def audit_summary():
    dias = request.args.get("dias", 7)
    limite = request.args.get("limite", 20)
    return jsonify(construir_resumen_auditoria(dias=dias, limite=limite))


@audit_bp.get("/eventos")
@role_required("ADMIN")
def audit_events():
    limite = min(max(int(request.args.get("limite", 50)), 1), 100)
    eventos = AuditEvent.query.order_by(AuditEvent.created_at.desc()).limit(limite).all()
    return jsonify(eventos=[evento.to_dict() for evento in eventos])


@audit_bp.get("/volumetria")
@role_required("ADMIN")
def audit_volumetria():
    dias = request.args.get("dias", 7)
    resumen = construir_resumen_auditoria(dias=dias, limite=1)
    return jsonify({
        "serie_diaria": resumen["serie_diaria"],
        "categorias": resumen["categorias"],
        "eventos_por_tipo": resumen["eventos_por_tipo"]
    })


@audit_bp.get("/seguridad")
@role_required("ADMIN")
def audit_seguridad():
    limite = min(max(int(request.args.get("limite", 50)), 1), 100)
    eventos = AuditEvent.query.filter(
        AuditEvent.category.in_(["auth", "seguridad", "admin", "users"])
    ).order_by(AuditEvent.created_at.desc()).limit(limite).all()
    return jsonify(eventos=[evento.to_dict() for evento in eventos])


@audit_bp.get("/errores")
@role_required("ADMIN")
def audit_errores():
    limite = min(max(int(request.args.get("limite", 50)), 1), 100)
    eventos = AuditEvent.query.filter(
        AuditEvent.category == "errores"
    ).order_by(AuditEvent.created_at.desc()).limit(limite).all()
    return jsonify(eventos=[evento.to_dict() for evento in eventos])
