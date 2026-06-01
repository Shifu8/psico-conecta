FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements/ requirements/
COPY backend/puerta-enlace-api/ app/
RUN pip install --no-cache-dir -r requirements/base.txt && pip install --no-cache-dir flask-cors
ENV PORT=5000
EXPOSE 5000
CMD ["python", "app/aplicacion.py"]
