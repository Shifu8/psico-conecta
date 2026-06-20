from datetime import datetime, timedelta
import pytz

def generar_slots(hora_inicio, hora_fin, duracion_slot_minutos):
    """
    Genera una lista de tuplas (inicio, fin) para cada slot dentro del bloque.
    """
    slots = []
    actual = hora_inicio
    
    # Asegurarnos que actual y hora_fin sean datetime.time para la comparación, pero 
    # necesitamos hacer cálculos con datetime.
    
    # Creamos objetos datetime artificiales solo para el cálculo de intervalos
    dt_actual = datetime.combine(datetime.today(), actual)
    dt_fin = datetime.combine(datetime.today(), hora_fin)
    
    delta = timedelta(minutes=duracion_slot_minutos)
    
    while dt_actual + delta <= dt_fin:
        slot_fin = dt_actual + delta
        slots.append({
            'hora_inicio': dt_actual.time().isoformat(),
            'hora_fin': slot_fin.time().isoformat()
        })
        dt_actual = slot_fin
        
    return slots

def parse_iso_datetime(dt_str):
    """Convierte un string ISO a un objeto datetime con zona horaria UTC."""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pytz.UTC)
        return dt
    except ValueError:
        return None
