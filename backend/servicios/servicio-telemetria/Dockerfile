FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements/ /requirements/
COPY backend/requirements-comunes.txt .
COPY backend/servicios/servicio-telemetria/ app/
RUN pip install --no-cache-dir -r app/requirements.txt
ENV PORT=5006
EXPOSE 5006
CMD ["python", "app/ejecutar.py"]
