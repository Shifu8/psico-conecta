# Archivo: datos_iniciales.py
# Descripción: Poblado de datos iniciales para la base de datos.
# Módulo: Servicio Usuarios

from aplicacion import create_app
from aplicacion.extensiones import db
from aplicacion.modelos import Permission, Role, User
from aplicacion.utilidades.seguridad import hash_password

PERMISSIONS = {
    "manage_users": "Crear, editar y desactivar usuarios.",
    "manage_roles": "Gestionar roles y permisos.",
    "view_all_profiles": "Consultar todos los perfiles.",
    "manage_user_status": "Activar o desactivar usuarios.",
    "view_own_profile": "Consultar el perfil propio.",
    "edit_own_profile": "Editar el perfil propio.",
    "future_appointments": "Acceder al modulo futuro de citas.",
    "future_teleconsultations": "Acceder al modulo futuro de teleconsultas.",
}

ROLES = {
    "ADMIN": ["manage_users", "manage_roles", "view_all_profiles", "manage_user_status"],
    "PSYCHOLOGIST": [
        "view_own_profile",
        "edit_own_profile",
        "future_appointments",
        "future_teleconsultations",
    ],
    "PATIENT": [
        "view_own_profile",
        "edit_own_profile",
        "future_appointments",
        "future_teleconsultations",
    ],
}

DEMO_USERS = [
    ("Admin", "PsicoConecta", "admin@psicoconecta.com", "Admin123*", "ADMIN"),
    (
        "Psicologo",
        "Demo",
        "psicologo@psicoconecta.com",
        "Psicologo123*",
        "PSYCHOLOGIST",
    ),
    (
        "Laura",
        "Gómez",
        "laura@psicoconecta.com",
        "Psicologo123*",
        "PSYCHOLOGIST",
    ),
    ("Paciente", "Demo", "paciente@psicoconecta.com", "Paciente123*", "PATIENT"),
]


def seed_database():
    db.create_all()
    permissions = {}
    for name, description in PERMISSIONS.items():
        permission = Permission.query.filter_by(name=name).first()
        if not permission:
            permission = Permission(name=name, description=description)
            db.session.add(permission)
        permissions[name] = permission

    roles = {}
    for name, permission_names in ROLES.items():
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name, description=f"Rol {name}")
            db.session.add(role)
        role.permissions = [permissions[item] for item in permission_names]
        roles[name] = role
    db.session.commit()

    for first_name, last_name, email, password, role_name in DEMO_USERS:
        if not User.query.filter_by(email=email).first():
            db.session.add(
                User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password_hash=hash_password(password),
                    role=roles[role_name],
                )
            )
    db.session.commit()


if __name__ == "__main__":
    application = create_app()
    with application.app_context():
        seed_database()
        print("Seed completado. Usuarios demo disponibles.")


