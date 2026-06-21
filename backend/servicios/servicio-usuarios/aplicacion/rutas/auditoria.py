from flask import Blueprint, jsonify, request

from aplicacion.intermediarios.roles import role_required
from aplicacion.modelos import AuditEvent
from aplicacion.servicios.servicio_auditoria import construir_resumen_auditoria

audit_bp = Blueprint("auditoria", __name__, url_prefix="/api/usuarios/auditoria")


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
