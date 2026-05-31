from datetime import timedelta

from flask_jwt_extended import create_access_token

from aplicacion.extensiones import db
from aplicacion.modelos import PasswordResetToken, Role, User
from aplicacion.utilidades.jwt import generate_reset_token, hash_token
from aplicacion.utilidades.seguridad import check_password, hash_password
from aplicacion.utilidades.tiempo import utc_now


def register_user(data):
    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        raise ValueError("Ya existe un usuario con ese correo.")
    role = Role.query.filter_by(name="PATIENT").first()
    if not role:
        raise RuntimeError("Ejecuta datos_iniciales.py para crear los roles iniciales.")
    user = User(
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
        email=email,
        password_hash=hash_password(data["password"]),
        phone=data.get("phone"),
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(data):
    user = User.query.filter_by(email=data["email"].strip().lower()).first()
    if not user or not check_password(user.password_hash, data["password"]):
        raise ValueError("Correo o contrasena incorrectos.")
    if user.status != "active":
        raise ValueError("Tu cuenta se encuentra inactiva.")
    token = create_access_token(
        identity=str(user.id), additional_claims={"role": user.role.name}
    )
    return user, token


def create_password_reset(email):
    user = User.query.filter_by(email=email.strip().lower()).first()
    if not user:
        return None
    raw_token = generate_reset_token()
    reset = PasswordResetToken(
        token_hash=hash_token(raw_token),
        user=user,
        expires_at=utc_now() + timedelta(minutes=30),
    )
    db.session.add(reset)
    db.session.commit()
    return raw_token


def reset_password(token, new_password):
    reset = PasswordResetToken.query.filter_by(token_hash=hash_token(token)).first()
    if not reset or not reset.is_active:
        raise ValueError("El token de recuperacion es invalido o expiro.")
    reset.user.password_hash = hash_password(new_password)
    reset.used_at = utc_now()
    db.session.commit()
    return reset.user

