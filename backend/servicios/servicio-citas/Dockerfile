FROM python:3.11-slim

WORKDIR /backend/servicios/servicio-citas

COPY backend/requirements/ /backend/requirements/
COPY backend/servicios/servicio-citas/ /backend/servicios/servicio-citas/

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=5002
EXPOSE 5002

CMD ["python", "ejecutar.py"]
