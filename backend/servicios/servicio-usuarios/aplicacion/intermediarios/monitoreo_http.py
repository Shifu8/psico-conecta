import time
from flask import request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from aplicacion.servicios.servicio_auditoria import registrar_evento_auditoria

def iniciar_monitoreo(app):
    @app.before_request
    def antes_de_peticion():
        g.inicio_peticion = time.time()

    @app.after_request
    def despues_de_peticion(response):
        if not hasattr(g, 'inicio_peticion'):
            return response
        
        # Ignorar OPTIONS y health checks para no spamear
        if request.method == "OPTIONS" or request.path.startswith("/health") or not request.path.startswith("/api/"):
            return response

        tiempo_ms = (time.time() - g.inicio_peticion) * 1000
        
        # Obtener identidad silenciosamente
        actor_email = None
        rol = None
        try:
            verify_jwt_in_request(optional=True)
            identidad = get_jwt_identity()
            if isinstance(identidad, dict):
                actor_email = identidad.get("email")
                rol = identidad.get("role")
        except Exception:
            pass

        status = "success"
        event_type = "api_request"
        category = "rendimiento"
        
        if response.status_code >= 400:
            status = "failure"
            category = "errores"
            if response.status_code == 401:
                event_type = "auth_failed"
            elif response.status_code == 403:
                event_type = "access_denied"
            elif response.status_code >= 500:
                event_type = "server_error"
            else:
                event_type = "client_error"

        # Determinar módulo por la ruta
        modulo = "sistema"
        if "citas" in request.path: modulo = "citas"
        elif "pagos" in request.path: modulo = "pagos"
        elif "teleconsulta" in request.path: modulo = "teleconsulta"
        elif "iot" in request.path: modulo = "iot"
        elif "auth" in request.path: modulo = "auth"
        elif "usuarios" in request.path: modulo = "usuarios"
        
        # Guardar en DB únicamente eventos importantes (evitar saturación de api_request y client_error)
        if event_type not in ["api_request", "client_error"]:
            registrar_evento_auditoria(
                event_type=event_type,
                category=category,
                status=status,
                actor_email=actor_email,
                request_obj=request,
                modulo=modulo,
                rol=rol,
                metodo_http=request.method,
                endpoint=request.path,
                codigo_respuesta=response.status_code,
                tiempo_respuesta_ms=tiempo_ms,
                descripcion=f"Acceso a {request.path} finalizado con {response.status_code}."
            )
        return response
