from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from aplicacion.extensiones import db
from aplicacion.intermediarios.autenticacion import get_current_user
from aplicacion.intermediarios.roles import role_required
from aplicacion.modelos import User
from aplicacion.esquemas.usuario import UserStatusSchema, UserUpdateSchema
from aplicacion.servicios.servicio_usuario import set_user_status, update_user

users_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


@users_bp.get("")
@role_required("ADMIN")
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify(users=[user.to_dict() for user in users])


@users_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    current_user = get_current_user()
    if not current_user or current_user.status != "active":
        return jsonify(message="Usuario inactivo o inexistente."), 403
    if current_user.id != user_id and current_user.role.name != "ADMIN":
        return jsonify(message="No tienes permisos para consultar este perfil."), 403
    user = db.get_or_404(User, user_id, description="Usuario no encontrado.")
    return jsonify(user=user.to_dict())


@users_bp.put("/<int:user_id>")
@jwt_required()
def edit_user(user_id):
    current_user = get_current_user()
    if not current_user or current_user.status != "active":
        return jsonify(message="Usuario inactivo o inexistente."), 403
    is_admin = current_user.role.name == "ADMIN"
    if current_user.id != user_id and not is_admin:
        return jsonify(message="No tienes permisos para editar este perfil."), 403
    data = UserUpdateSchema().load(request.get_json(silent=True) or {})
    if "role" in data and not is_admin:
        return jsonify(message="Solo un administrador puede cambiar roles."), 403
    user = db.get_or_404(User, user_id, description="Usuario no encontrado.")
    return jsonify(message="Perfil actualizado.", user=update_user(user, data, is_admin).to_dict())


@users_bp.delete("/<int:user_id>")
@role_required("ADMIN")
def delete_user(user_id):
    user = db.get_or_404(User, user_id, description="Usuario no encontrado.")
    return jsonify(
        message="Usuario desactivado.", user=set_user_status(user, "inactive").to_dict()
    )


@users_bp.patch("/<int:user_id>/status")
@role_required("ADMIN")
def change_status(user_id):
    data = UserStatusSchema().load(request.get_json(silent=True) or {})
    user = db.get_or_404(User, user_id, description="Usuario no encontrado.")
    return jsonify(
        message="Estado actualizado.", user=set_user_status(user, data["status"]).to_dict()
    )


