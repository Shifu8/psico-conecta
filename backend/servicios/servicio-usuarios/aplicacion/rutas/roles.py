from flask import Blueprint, jsonify, request

from aplicacion.extensiones import db
from aplicacion.intermediarios.roles import role_required
from aplicacion.modelos import Permission, Role
from aplicacion.esquemas.rol import RoleSchema

roles_bp = Blueprint("roles", __name__, url_prefix="/api/usuarios/roles")


def _set_permissions(role, permission_names):
    permissions = Permission.query.filter(Permission.name.in_(permission_names)).all()
    if len(permissions) != len(set(permission_names)):
        raise ValueError("Uno o mas permisos no existen.")
    role.permissions = permissions


@roles_bp.get("")
@role_required("ADMIN")
def list_roles():
    return jsonify(roles=[role.to_dict() for role in Role.query.order_by(Role.name).all()])


@roles_bp.post("")
@role_required("ADMIN")
def create_role():
    data = RoleSchema().load(request.get_json(silent=True) or {})
    name = data["name"].strip().upper()
    if Role.query.filter_by(name=name).first():
        raise ValueError("El rol ya existe.")
    role = Role(name=name, description=data["description"])
    _set_permissions(role, data["permissions"])
    db.session.add(role)
    db.session.commit()
    return jsonify(message="Rol creado.", role=role.to_dict()), 201


@roles_bp.put("/<int:role_id>")
@role_required("ADMIN")
def update_role(role_id):
    role = db.get_or_404(Role, role_id, description="Rol no encontrado.")
    data = RoleSchema().load(request.get_json(silent=True) or {})
    role.name = data["name"].strip().upper()
    role.description = data["description"]
    _set_permissions(role, data["permissions"])
    db.session.commit()
    return jsonify(message="Rol actualizado.", role=role.to_dict())


@roles_bp.delete("/<int:role_id>")
@role_required("ADMIN")
def delete_role(role_id):
    role = db.get_or_404(Role, role_id, description="Rol no encontrado.")
    if role.users:
        return jsonify(message="No se puede eliminar un rol asignado a usuarios."), 409
    db.session.delete(role)
    db.session.commit()
    return jsonify(message="Rol eliminado.")


