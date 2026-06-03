import os

from aplicacion.extensiones import db
from aplicacion.modelos.permiso import role_permissions

_SCHEMA = os.environ.get("DATABASE_SCHEMA", "usuarios_schema") or None


class Role(db.Model):
    __tablename__ = "roles"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")
    permissions = db.relationship(
        "Permission", secondary=role_permissions, lazy="select", backref="roles"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": [permission.name for permission in self.permissions],
        }


