from aplicacion.rutas.auditoria import audit_bp
from aplicacion.rutas.autenticacion import auth_bp
from aplicacion.rutas.paneles import dashboard_bp
from aplicacion.rutas.roles import roles_bp
from aplicacion.rutas.usuarios import users_bp

__all__ = ["audit_bp", "auth_bp", "dashboard_bp", "roles_bp", "users_bp"]
