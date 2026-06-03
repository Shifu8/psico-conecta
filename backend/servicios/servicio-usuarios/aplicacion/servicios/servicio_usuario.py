from aplicacion.extensiones import db
from aplicacion.modelos import Role
from aplicacion.utilidades.validacion import normalize_phone, normalize_spaces


def update_user(user, data, allow_role=False):
    for field in ("first_name", "last_name", "phone"):
        if field in data:
            value = data[field]
            if field in ("first_name", "last_name"):
                value = normalize_spaces(value)
            if field == "phone":
                value = normalize_phone(value)
            setattr(user, field, value)
    if allow_role and "role" in data:
        role = Role.query.filter_by(name=data["role"]).first()
        if not role:
            raise ValueError("El rol solicitado no existe.")
        user.role = role
    db.session.commit()
    return user


def set_user_status(user, status):
    user.status = status
    db.session.commit()
    return user

