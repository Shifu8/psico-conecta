import os

from aplicacion.extensiones import db

_SCHEMA = os.environ.get("DATABASE_SCHEMA", "usuarios_schema") or None

role_permissions = db.Table(
    "roles_permisos",
    db.Column(
        "rol_id",
        db.Integer,
        db.ForeignKey(f"{_SCHEMA + '.' if _SCHEMA else ''}roles.id"),
        primary_key=True,
    ),
    db.Column(
        "permiso_id",
        db.Integer,
        db.ForeignKey(f"{_SCHEMA + '.' if _SCHEMA else ''}permisos.id"),
        primary_key=True,
    ),
    schema=_SCHEMA if _SCHEMA else None,
)


class Permission(db.Model):
    __tablename__ = "permisos"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


