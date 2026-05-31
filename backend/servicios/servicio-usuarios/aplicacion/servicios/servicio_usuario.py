from aplicacion.extensiones import db
from aplicacion.modelos import Role, User


def update_user(user, data, allow_role=False):
    for field in ("first_name", "last_name", "phone"):
        if field in data:
            setattr(user, field, data[field])
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


