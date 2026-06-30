# Archivo: servicio_auditoria.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Usuarios

import json
from collections import Counter, defaultdict
from datetime import timedelta

from flask import current_app

from aplicacion.extensiones import db
from aplicacion.modelos import AuditEvent
from aplicacion.utilidades.tiempo import utc_now


MAPEO_EVENTOS = {
    "login_success": {"accion": "Inicio de sesión local exitoso", "severidad": "Baja", "canal": "Web", "modulo": "Usuarios"},
    "login_failed": {"accion": "Inicio de sesión local fallido", "severidad": "Media", "canal": "Web", "modulo": "Usuarios"},
    "login_blocked": {"accion": "Bloqueo preventivo", "severidad": "Alta", "canal": "Web", "modulo": "Seguridad"},
    "google_login_success": {"accion": "Inicio de sesión con Google exitoso", "severidad": "Baja", "canal": "Google OAuth", "modulo": "Usuarios"},
    "google_login_failed": {"accion": "Inicio de sesión con Google fallido", "severidad": "Media", "canal": "Google OAuth", "modulo": "Usuarios"},
    "google_register_success": {"accion": "Registro exitoso", "severidad": "Baja", "canal": "Google OAuth", "modulo": "Usuarios"},
    "register_success": {"accion": "Registro exitoso", "severidad": "Baja", "canal": "Web", "modulo": "Usuarios"},
    "register_failed": {"accion": "Registro fallido", "severidad": "Media", "canal": "Web", "modulo": "Usuarios"},
    "password_reset_requested": {"accion": "Solicitud de recuperación de contraseña", "severidad": "Media", "canal": "Web", "modulo": "Usuarios"},
    "password_reset_success": {"accion": "Restablecimiento de contraseña exitoso", "severidad": "Baja", "canal": "Web", "modulo": "Usuarios"},
    "logout": {"accion": "Cierre de sesión", "severidad": "Baja", "canal": "Web", "modulo": "Usuarios"},
    "admin_user_updated": {"accion": "Usuario actualizado", "severidad": "Baja", "canal": "Sistema", "modulo": "Usuarios"},
    "admin_user_status_changed": {"accion": "Cambio de estado de usuario", "severidad": "Media", "canal": "Sistema", "modulo": "Usuarios"},
    "admin_user_deactivated": {"accion": "Usuario eliminado", "severidad": "Alta", "canal": "Sistema", "modulo": "Usuarios"},
    "turnstile_success": {"accion": "Validación Turnstile exitosa", "severidad": "Informativo", "canal": "Web", "modulo": "Seguridad"},
    "turnstile_failed": {"accion": "Validación Turnstile fallida", "severidad": "Alta", "canal": "Web", "modulo": "Seguridad"},
    "auth_failed": {"accion": "Token inválido o acceso sin auth", "severidad": "Media", "canal": "API", "modulo": "Autenticación"},
    "access_denied": {"accion": "Acceso denegado por rol", "severidad": "Alta", "canal": "API", "modulo": "Autenticación"},
    "server_error": {"accion": "Error interno del servidor", "severidad": "Crítica", "canal": "API", "modulo": "Sistema"},
    "client_error": {"accion": "Petición de cliente inválida", "severidad": "Baja", "canal": "API", "modulo": "Sistema"},
    "api_request": {"accion": "Petición API", "severidad": "Baja", "canal": "API", "modulo": "Sistema"},
    "profile_photo_updated": {"accion": "Foto de perfil actualizada", "severidad": "Baja", "canal": "Web", "modulo": "Usuarios"},
    "profile_photo_deleted": {"accion": "Foto de perfil eliminada", "severidad": "Baja", "canal": "Web", "modulo": "Usuarios"},
    "user_profile_updated": {"accion": "Perfil de usuario actualizado", "severidad": "Baja", "canal": "Web", "modulo": "Usuarios"},
    "cita_scheduled": {"accion": "Cita agendada", "severidad": "Baja", "canal": "Web", "modulo": "Citas"},
    "cita_cancelled": {"accion": "Cita cancelada", "severidad": "Media", "canal": "Web", "modulo": "Citas"},
    "cita_confirmed": {"accion": "Cita confirmada", "severidad": "Baja", "canal": "Web", "modulo": "Citas"},
}


def _ip_cliente(request_obj):
    if not request_obj:
        return None
    forwarded_for = request_obj.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()[:64]
    return (request_obj.remote_addr or "")[:64] or None


def _user_agent(request_obj):
    if not request_obj:
        return None
    return (request_obj.headers.get("User-Agent") or "")[:255] or None


def _detalle_json(detail):
    if not detail:
        return None
    return json.dumps(detail, ensure_ascii=False, default=str)


def registrar_evento_auditoria(
    event_type,
    category,
    *,
    status="success",
    actor=None,
    target=None,
    actor_email=None,
    target_email=None,
    detail=None,
    request_obj=None,
    modulo=None,
    rol=None,
    metodo_http=None,
    endpoint=None,
    codigo_respuesta=None,
    tiempo_respuesta_ms=None,
    descripcion=None,
    severidad=None,
    canal=None,
    accion=None,
):
    try:
        mapeo = MAPEO_EVENTOS.get(event_type, {})
        if not accion: accion = mapeo.get("accion", event_type)
        if not severidad: severidad = mapeo.get("severidad", "Baja")
        if not canal: canal = mapeo.get("canal", "API")
        if not modulo: modulo = mapeo.get("modulo", "Sistema")

        detail_dict = detail if isinstance(detail, dict) else ({"valor": detail} if detail else {})
        if modulo: detail_dict["modulo"] = modulo
        if rol: detail_dict["rol"] = rol
        if metodo_http: detail_dict["metodo_http"] = metodo_http
        if endpoint: detail_dict["endpoint"] = endpoint
        if codigo_respuesta is not None: detail_dict["codigo_respuesta"] = codigo_respuesta
        if tiempo_respuesta_ms is not None: detail_dict["tiempo_respuesta_ms"] = round(tiempo_respuesta_ms, 2)
        if descripcion: detail_dict["descripcion"] = descripcion
        if severidad: detail_dict["severidad"] = severidad
        if canal: detail_dict["canal"] = canal
        if accion: detail_dict["accion"] = accion

        event = AuditEvent(
            event_type=event_type,
            category=category,
            status=status,
            actor_user_id=getattr(actor, "id", None),
            target_user_id=getattr(target, "id", None),
            actor_email=actor_email or getattr(actor, "email", None),
            target_email=target_email or getattr(target, "email", None),
            ip_address=_ip_cliente(request_obj),
            user_agent=_user_agent(request_obj),
            detail=_detalle_json(detail_dict) if detail_dict else None,
        )
        db.session.add(event)
        db.session.commit()
        return event
    except Exception as error:  # pragma: no cover - la auditoria no debe tumbar el flujo principal
        db.session.rollback()
        current_app.logger.exception("No fue posible registrar auditoria: %s", error)
        return None


def construir_resumen_auditoria(*, dias=7, limite=20):
    dias = min(max(int(dias), 1), 90)
    limite = min(max(int(limite), 1), 100)
    desde = utc_now() - timedelta(days=dias)
    eventos_periodo = (
        AuditEvent.query.filter(AuditEvent.created_at >= desde)
        .order_by(AuditEvent.created_at.desc())
        .all()
    )
    recientes = eventos_periodo[:limite]

    tipos = Counter(event.event_type for event in eventos_periodo)
    categorias = Counter(event.category for event in eventos_periodo)
    estados = Counter(event.status for event in eventos_periodo)
    serie = _serie_diaria(eventos_periodo, dias)

    return {
        "periodo_dias": dias,
        "metricas": {
            "eventos": len(eventos_periodo),
            "inicios_sesion": tipos["login_success"] + tipos["google_login_success"],
            "inicios_fallidos": tipos["login_failed"] + tipos["login_blocked"],
            "registros": tipos["register_success"] + tipos["google_register_success"],
            "cambios_administrativos": sum(
                cantidad
                for tipo, cantidad in tipos.items()
                if tipo.startswith("admin_")
            ),
            "cierres_sesion": tipos["logout"],
            "eventos_exitosos": estados["success"],
            "eventos_fallidos": estados["failure"],
        },
        "categorias": [
            {"categoria": categoria, "total": total}
            for categoria, total in categorias.most_common()
        ],
        "eventos_por_tipo": [
            {"tipo": tipo, "total": total}
            for tipo, total in tipos.most_common()
        ],
        "serie_diaria": serie,
        "eventos_recientes": [event.to_dict() for event in recientes],
    }


def _serie_diaria(eventos, dias):
    hoy = utc_now().date()
    puntos = {
        (hoy - timedelta(days=offset)).isoformat(): {
            "fecha": (hoy - timedelta(days=offset)).isoformat(),
            "accesos": 0,
            "fallos": 0,
            "registros": 0,
            "administracion": 0,
        }
        for offset in range(dias - 1, -1, -1)
    }
    grupos = defaultdict(int)
    for event in eventos:
        fecha = event.created_at.date().isoformat()
        if event.event_type in ("login_success", "google_login_success"):
            grupos[(fecha, "accesos")] += 1
        elif event.event_type in ("login_failed", "login_blocked"):
            grupos[(fecha, "fallos")] += 1
        elif event.event_type in ("register_success", "google_register_success"):
            grupos[(fecha, "registros")] += 1
        elif event.event_type.startswith("admin_"):
            grupos[(fecha, "administracion")] += 1

    for (fecha, campo), total in grupos.items():
        if fecha in puntos:
            puntos[fecha][campo] = total
    return list(puntos.values())
