# Archivo: Dockerfile
# Descripción: Receta de construcción de contenedor Docker.
# Módulo: Servicio Citas

FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements/ /requirements/
COPY backend/servicios/servicio-citas/ app/
RUN pip install --no-cache-dir -r app/requirements.txt
ENV PORT=5002
EXPOSE 5002
CMD ["python", "app/aplicacion.py"]
