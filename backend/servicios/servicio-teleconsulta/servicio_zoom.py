# Archivo: servicio_zoom.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Teleconsultas

def obtener_token_acceso_zoom():
    """Obtiene un token cuando se configuren credenciales Zoom Server-to-Server."""
    return None


def crear_reunion_zoom(datos):
    """Prepara una reunion demostrativa hasta habilitar Zoom API."""
    return {
        "zoom_meeting_id": "demo-reunion-zoom",
        "cita_id": datos.get("cita_id"),
        "tema": datos.get("tema", "Teleconsulta PsicoConecta"),
        "enlace_acceso": None,
        "estado": "pendiente_configuracion_zoom",
    }
