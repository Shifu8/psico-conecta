FROM python:3.11-slim

WORKDIR /backend/servicios/servicio-teleconsulta
COPY backend/requirements/ /backend/requirements/
COPY backend/servicios/servicio-teleconsulta/ /backend/servicios/servicio-teleconsulta/
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=5003
EXPOSE 5003
CMD ["sh", "-c", "python preparar_bd.py && exec python ejecutar.py"]
