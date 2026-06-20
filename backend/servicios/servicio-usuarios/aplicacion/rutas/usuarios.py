from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_file
from flask_jwt_extended import jwt_required

from aplicacion.extensiones import db
from aplicacion.intermediarios.autenticacion import get_current_user
from aplicacion.intermediarios.roles import role_required
from aplicacion.modelos import User
from aplicacion.esquemas.usuario import UserStatusSchema, UserUpdateSchema
from aplicacion.servicios.servicio_usuario import set_user_status, update_user
from aplicacion.utilidades.tiempo import utc_now

users_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")

_FOTO_MAX_BYTES = 2 * 1024 * 1024
_FOTO_MIMES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
_FOTO_EXTENSIONES = tuple(dict.fromkeys(_FOTO_MIMES.values()))


def _directorio_fotos_perfil():
    directorio = Path(current_app.instance_path) / "fotos_perfil"
    directorio.mkdir(parents=True, exist_ok=True)
    return directorio


def _buscar_foto_perfil(user_id):
    directorio = Path(current_app.instance_path) / "fotos_perfil"
    for extension in _FOTO_EXTENSIONES:
        ruta = directorio / f"usuario_{user_id}{extension}"
        if ruta.exists():
            return ruta
    return None


def _eliminar_fotos_perfil(user_id):
    directorio = Path(current_app.instance_path) / "fotos_perfil"
    for extension in _FOTO_EXTENSIONES:
        ruta = directorio / f"usuario_{user_id}{extension}"
        if ruta.exists():
            ruta.unlink()


def _usuario_puede_editar_perfil(current_user, user_id):
    return current_user.id == user_id or current_user.role.name == "ADMIN"


def _validar_usuario_activo():
    current_user = get_current_user()
    if not current_user or current_user.status != "active":
        return None, (jsonify(message="Usuario inactivo o inexistente."), 403)
    return current_user, None


@users_bp.get("")
@role_required("ADMIN")
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify(users=[user.to_dict() for user in users])


@users_bp.get("/<int:user_id>/foto-perfil")
def get_profile_photo(user_id):
    ruta = _buscar_foto_perfil(user_id)
    if not ruta:
        return jsonify(message="Foto de perfil no encontrada."), 404
    mimetype = next(
        (tipo for tipo, extension in _FOTO_MIMES.items() if extension == ruta.suffix),
        "application/octet-stream",
    )
    return send_file(ruta, mimetype=mimetype, conditional=True, max_age=3600)


@users_bp.post("/<int:user_id>/foto-perfil")
@jwt_required()
def upload_profile_photo(user_id):
    current_user, error = _validar_usuario_activo()
    if error:
        return error
    if not _usuario_puede_editar_perfil(current_user, user_id):
        return jsonify(message="No tienes permisos para editar este perfil."), 403

    user = db.get_or_404(User, user_id, description="Usuario no encontrado.")
    archivo = (
        request.files.get("foto")
        or request.files.get("photo")
        or request.files.get("image")
    )
    if not archivo:
        return jsonify(message="Selecciona una imagen para subir."), 400

    extension = _FOTO_MIMES.get((archivo.mimetype or "").lower())
    if not extension:
        return jsonify(message="La foto debe ser una imagen JPG, PNG o WebP."), 400

    contenido = archivo.read()
    if not contenido:
        return jsonify(message="La imagen esta vacia."), 400
    if len(contenido) > _FOTO_MAX_BYTES:
        return jsonify(message="La imagen no debe superar 2 MB."), 413

    _eliminar_fotos_perfil(user.id)
    ruta = _directorio_fotos_perfil() / f"usuario_{user.id}{extension}"
    ruta.write_bytes(contenido)
    user.updated_at = utc_now()
    db.session.commit()
    return jsonify(message="Foto de perfil actualizada.", user=user.to_dict())


@users_bp.delete("/<int:user_id>/foto-perfil")
@jwt_required()
def delete_profile_photo(user_id):
    current_user, error = _validar_usuario_activo()
    if error:
        return error
    if not _usuario_puede_editar_perfil(current_user, user_id):
        return jsonify(message="No tienes permisos para editar este perfil."), 403

    user = db.get_or_404(User, user_id, description="Usuario no encontrado.")
    _eliminar_fotos_perfil(user.id)
    user.updated_at = utc_now()
    db.session.commit()
    return jsonify(message="Foto de perfil eliminada.", user=user.to_dict())


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
    if not data:
        raise ValueError("Envia al menos un campo para actualizar el perfil.")
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