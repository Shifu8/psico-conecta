# Servicio de Pagos

## Objetivo
Simular pagos y transacciones con Stripe Sandbox para PsicoConecta.

## Responsabilidades
- Crear pagos simulados
- Listar pagos registrados
- Preparar el terreno para Stripe Sandbox

## Endpoints
- `POST /api/pagos/crear-pago`
- `GET /api/pagos`

## Variables de entorno
- `DATABASE_URL`
- `DATABASE_SCHEMA=pagos_schema`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_ACCESS_TOKEN_EXPIRES`
- `STRIPE_API_KEY` (futuro)

## Dependencias
- `-r ../../requirements/pagos.txt`

## Base de datos
- PostgreSQL
- Esquema: `pagos_schema`
- Tablas iniciales: `pagos`, `transacciones`, `comprobantes`

## Ejecución
```powershell
cd backend\servicios\servicio-pagos
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python aplicacion.py
```
