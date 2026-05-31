from flask_jwt_extended import get_jwt_identity

from aplicacion.extensiones import db
from aplicacion.modelos import User


def get_current_user():
    identity = get_jwt_identity()
    return db.session.get(User, int(identity)) if identity else None


