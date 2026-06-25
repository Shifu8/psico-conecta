# Archivo: __init__.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio Citas

from .rutas_citas import bp_citas
from .rutas_disponibilidad import bp_disponibilidad

__all__ = ['bp_citas', 'bp_disponibilidad']
