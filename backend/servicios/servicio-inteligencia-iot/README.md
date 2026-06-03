# Servicio Inteligente e IoT

## Objetivo
Registrar lecturas IoT y datos emocionales con integración a AWS DynamoDB y AWS IoT Core.

## Responsabilidades
- Recibir emociones y lecturas IoT
- Listar datos registrados
- Preparar la configuración de AWS DynamoDB
- Simular la integración con MQTT y WebSockets

## Endpoints
- `GET|POST /api/iot/emociones`
- `GET|POST /api/iot/lecturas`
- `GET /api/iot/configuracion`

## Variables de entorno
- `AWS_REGION`
- `AWS_ACCESS_KEY_ID` (futuro)
- `AWS_SECRET_ACCESS_KEY` (futuro)
- `AWS_SESSION_TOKEN` (futuro)
- `DYNAMODB_TABLE_EMOCIONES=emociones`
- `DYNAMODB_TABLE_LECTURAS=lecturas_iot`
- `DYNAMODB_TABLE_NOTIFICACIONES=notificaciones`
- `DYNAMODB_TABLE_LOGS=logs_iot`

## Dependencias
- `-r ../../requirements/iot.txt`

## Base de datos
- DynamoDB para IoT y datos flexibles
- Tablas esperadas: `emociones`, `lecturas_iot`, `notificaciones`, `logs_iot`

## Ejecución
```powershell
cd backend\servicios\servicio-inteligencia-iot
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python aplicacion.py
```
