# Servicio de Teleconsulta

## Objetivo
Proveer endpoints para gestionar teleconsultas y reuniones con Zoom en PsicoConecta.

## Responsabilidades
- Crear reuniones de teleconsulta
- Listar sesiones existentes
- Integrar con Zoom API

## Endpoints
- `POST /api/teleconsulta/zoom/crear-reunion`
- `GET /api/teleconsulta/sesiones`

## Variables de entorno
- `DATABASE_URL`
- `DATABASE_SCHEMA=teleconsulta_schema`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_ACCESS_TOKEN_EXPIRES`
- `ZOOM_CLIENT_ID` (futuro)
- `ZOOM_CLIENT_SECRET` (futuro)

## Dependencias
- `-r ../../requirements/teleconsulta.txt`

## Base de datos
- PostgreSQL
- Esquema: `teleconsulta_schema`
- Tablas iniciales: `sesiones_zoom`, `historial_sesiones`

## Ejecución
```powershell
cd backend\servicios\servicio-teleconsulta
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python aplicacion.py
```
