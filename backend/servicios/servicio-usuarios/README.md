# Servicio de Usuarios

## Objetivo
Administrar la autenticación, autorización y perfil de usuarios de PsicoConecta.

## Responsabilidades
- Registro de usuarios
- Inicio de sesión con JWT
- Cierre de sesión y revocación de tokens
- Gestión de perfiles
- Roles y permisos
- Recuperación de contraseña con Gmail API
- Inicio de sesión con Google OAuth directo

## Endpoints
- `POST /api/usuarios/autenticacion/registro`
- `POST /api/usuarios/autenticacion/inicio-sesion`
- `POST /api/usuarios/autenticacion/cierre-sesion`
- `POST /api/usuarios/autenticacion/recuperar-contrasena`
- `POST /api/usuarios/autenticacion/restablecer-contrasena`
- `GET /api/usuarios/autenticacion/mi-perfil`
- `POST /api/usuarios/autenticacion/google`
- `GET /api/usuarios/autenticacion/google/configuracion`
- `GET /api/usuarios`
- `GET /api/usuarios/<id>`
- `PUT /api/usuarios/<id>`
- `DELETE /api/usuarios/<id>`
- `PATCH /api/usuarios/<id>/status`
- `GET|POST /api/usuarios/roles`
- `PUT|DELETE /api/usuarios/roles/<id>`

## Variables de entorno
- `DATABASE_URL`
- `DATABASE_SCHEMA=usuarios_schema`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_ACCESS_TOKEN_EXPIRES`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_LOGIN_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`
- `GOOGLE_SENDER_EMAIL`
- `FRONTEND_URL`
- `MODO_DESARROLLO=true`

## Dependencias
- `-r ../../requirements/usuarios.txt`

## Base de datos
- PostgreSQL
- Esquema: `usuarios_schema`
- Tablas iniciales: `usuarios`, `roles`, `permisos`, `roles_permisos`, `tokens_recuperacion`, `tokens_revocados`

## Ejecución
```powershell
cd backend\servicios\servicio-usuarios
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python datos_iniciales.py
python ejecutar.py
```
