FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements/ /requirements/
COPY backend/servicios/servicio-teleconsulta/ app/
RUN pip install --no-cache-dir -r app/requirements.txt
ENV PORT=5003
EXPOSE 5003
CMD ["python", "app/aplicacion.py"]
