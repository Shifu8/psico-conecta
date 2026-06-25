# Archivo: Dockerfile
# Descripción: Receta de construcción de contenedor Docker.
# Módulo: Puerta de Enlace

FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements/ /requirements/
COPY backend/requirements-comunes.txt .
COPY backend/puerta-enlace-api/ app/
RUN pip install --no-cache-dir -r app/requirements.txt
ENV PORT=5000
EXPOSE 5000
CMD ["python", "app/aplicacion.py"]
