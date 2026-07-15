# Servicio de pagos PsicoConecta
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements/ /requirements/
COPY backend/servicios/servicio-pagos/ /app/
RUN pip install --no-cache-dir -r /requirements/pagos.txt

ENV PORT=5004
EXPOSE 5004
CMD ["sh", "-c", "python preparar_bd.py && exec python ejecutar.py"]
