FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements/ requirements/
COPY backend/servicios/servicio-pagos/ app/
RUN pip install --no-cache-dir -r app/requirements.txt
ENV PORT=5004
EXPOSE 5004
CMD ["python", "app/aplicacion.py"]
