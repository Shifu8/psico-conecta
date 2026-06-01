FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements/ requirements/
COPY backend/servicios/servicio-usuarios/ app/
RUN pip install --no-cache-dir -r app/requirements.txt
ENV PORT=5001 FLASK_ENV=production
EXPOSE 5001
CMD ["python", "app/ejecutar.py"]
