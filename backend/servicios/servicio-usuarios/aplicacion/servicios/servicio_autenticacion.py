from datetime import timedelta

from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

from aplicacion.extensiones import db
from aplicacion.modelos import PasswordResetToken, Role, User
from aplicacion.utilidades.jwt import generate_reset_token, hash_token
from aplicacion.utilidades.seguridad import check_password, hash_password
from aplicacion.utilidades.tiempo import utc_now
from aplicacion.utilidades.validacion import normalize_phone, normalize_spaces


class InvalidCredentialsError(ValueError):
    pass


def register_user(data):
    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        raise ValueError("Ya existe un usuario con ese correo.")
    role = Role.query.filter_by(name="PATIENT").first()
    if not role:
        raise RuntimeError("Ejecuta datos_iniciales.py para crear los roles iniciales.")
    user = User(
        first_name=normalize_spaces(data["first_name"]),
        last_name=normalize_spaces(data["last_name"]),
        email=email,
        password_hash=hash_password(data["password"]),
        phone=normalize_phone(data.get("phone")),
        role=role,
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Ya existe un usuario con ese correo.") from None
    return user


def authenticate_user(data):
    user = User.query.filter_by(email=data["email"].strip().lower()).first()
    if not user or not check_password(user.password_hash, data["password"]):
        raise InvalidCredentialsError("Correo o contraseña incorrectos.")
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
    now = utc_now()
    PasswordResetToken.query.filter_by(user_id=user.id, used_at=None).update(
        {"used_at": now}
    )
    reset = PasswordResetToken(
        token_hash=hash_token(raw_token),
        user=user,
        expires_at=now + timedelta(minutes=30),
    )
    db.session.add(reset)
    db.session.commit()
    return raw_token


def reset_password(token, new_password):
    reset = PasswordResetToken.query.filter_by(token_hash=hash_token(token)).first()
    if not reset or not reset.is_active:
        raise ValueError("El token de recuperación es inválido o expiró.")
    reset.user.password_hash = hash_password(new_password)
    PasswordResetToken.query.filter_by(user_id=reset.user_id, used_at=None).update(
        {"used_at": utc_now()}
    )
    db.session.commit()
    return reset.user
