# Archivo: Dockerfile
# Descripción: Imagen del Servicio IoT + Telemetría WebSocket.
# Expone:
#   5005 → API REST Flask (emociones, lecturas, configuración)
#   5006 → Servidor WebSocket asyncio (ESP32 + clientes web)
# Módulo: Servicio Inteligencia e IoT

FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias compartidas primero para aprovechar la caché de Docker
COPY backend/requirements/ /requirements/
COPY backend/servicios/servicio-inteligencia-iot/ .

# Instalar todas las dependencias del módulo IoT
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=5005
ENV PORT_TELEMETRIA=5006
ENV PYTHONUNBUFFERED=1

EXPOSE 5005
EXPOSE 5006

# Arranca ambos procesos:
# 1. Flask REST en el puerto 5005 (background)
# 2. WebSocket de telemetría en el puerto 5006 (foreground)
CMD ["sh", "-c", "python aplicacion.py & cd telemetria && python ejecutar.py"]
