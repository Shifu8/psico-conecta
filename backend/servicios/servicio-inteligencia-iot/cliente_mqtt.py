# Archivo: cliente_mqtt.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Servicio IoT

def conectar_aws_iot_core():
    """Conecta exclusivamente con AWS IoT Core cuando existan credenciales."""
    return None


def publicar_lectura_sensor(datos):
    """Publica una lectura MQTT del ESP32 con MAX30102."""
    return {"estado": "pendiente_configuracion_aws_iot_core", "datos": datos}
