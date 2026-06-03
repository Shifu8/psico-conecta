# Servicio de Citas

## Objetivo
Gestionar la información de citas médicas y horarios disponibles en PsicoConecta.

## Responsabilidades
- Registrar nuevas citas
- Listar citas existentes
- Mantener horarios disponibles
- Almacenar historial de citas

## Endpoints
- `GET /api/citas`
- `POST /api/citas`

## Variables de entorno
- `DATABASE_URL`
- `DATABASE_SCHEMA=citas_schema`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_ACCESS_TOKEN_EXPIRES`

## Dependencias
- `-r ../../requirements/citas.txt`

## Base de datos
- PostgreSQL
- Esquema: `citas_schema`
- Tablas iniciales: `citas`, `horarios_disponibles`, `historial_citas`

## Ejecución
```powershell
cd backend\servicios\servicio-citas
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python aplicacion.py
```
