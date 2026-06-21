import json
from collections import Counter, defaultdict
from datetime import timedelta

from flask import current_app

from aplicacion.extensiones import db
from aplicacion.modelos import AuditEvent
from aplicacion.utilidades.tiempo import utc_now


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
):
    try:
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
            detail=_detalle_json(detail),
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
