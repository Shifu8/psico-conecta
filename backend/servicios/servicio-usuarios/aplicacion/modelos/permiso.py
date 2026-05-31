from aplicacion.extensiones import db


role_permissions = db.Table(
    "roles_permisos",
    db.Column(
        "rol_id",
        db.Integer,
        db.ForeignKey("usuarios_schema.roles.id"),
        primary_key=True,
    ),
    db.Column(
        "permiso_id",
        db.Integer,
        db.ForeignKey("usuarios_schema.permisos.id"),
        primary_key=True,
    ),
    schema="usuarios_schema",
)


class Permission(db.Model):
    __tablename__ = "permisos"
    __table_args__ = {"schema": "usuarios_schema"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


