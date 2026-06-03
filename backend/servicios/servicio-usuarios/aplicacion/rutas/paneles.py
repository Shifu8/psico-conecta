from flask import Blueprint, jsonify

from aplicacion.intermediarios.autenticacion import get_current_user
from aplicacion.intermediarios.roles import role_required

dashboard_bp = Blueprint("paneles", __name__, url_prefix="/api/usuarios")


def _dashboard(role, modules):
    return jsonify(role=role, user=get_current_user().to_dict(), modules=modules)


@dashboard_bp.get("/administrador/panel")
@role_required("ADMIN")
def admin_dashboard():
    return _dashboard("ADMIN", ["users", "roles", "reports"])


@dashboard_bp.get("/psicologo/panel")
@role_required("PSYCHOLOGIST")
def psychologist_dashboard():
    return _dashboard("PSYCHOLOGIST", ["appointments", "patients", "teleconsultations"])


@dashboard_bp.get("/paciente/panel")
@role_required("PATIENT")
def patient_dashboard():
    return _dashboard("PATIENT", ["appointments", "teleconsultations", "emotional_tracking"])


