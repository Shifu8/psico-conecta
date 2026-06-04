from aplicacion.extensiones import db
from aplicacion.modelos.schema import obtener_schema, prefijo_schema
from aplicacion.utilidades.tiempo import utc_now

_SCHEMA = obtener_schema()
_SCHEMA_PREFIX = prefijo_schema(_SCHEMA)


class User(db.Model):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = db.Column(db.Integer, primary_key=True)
    cognito_sub = db.Column(db.String(255), unique=True, nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    role_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{_SCHEMA_PREFIX}roles.id"),
        nullable=False,
    )
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )
    role = db.relationship("Role", backref=db.backref("users", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": f"{self.first_name} {self.last_name}",
            "email": self.email,
            "phone": self.phone,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "role": self.role.name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
