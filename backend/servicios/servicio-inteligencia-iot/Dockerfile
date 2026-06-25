# Archivo: Dockerfile
# Descripción: Receta de construcción de contenedor Docker.
# Módulo: Servicio IoT

FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements/ /requirements/
COPY backend/servicios/servicio-inteligencia-iot/ app/
RUN pip install --no-cache-dir -r app/requirements.txt
ENV PORT=5005
EXPOSE 5005
CMD ["python", "app/aplicacion.py"]
