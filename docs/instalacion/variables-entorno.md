# Variables de entorno

Descripción corta:
Este documento describe la gestión de credenciales y variables de configuración en los diferentes componentes de PsicoConecta, indicando qué archivos `.env` deben crearse y cómo administrarlos.

## 1. Principio de seguridad

El proyecto utiliza variables de entorno para manejar secretos, claves de APIs externas (como Zoom, Stripe, Google OAuth) y cadenas de conexión a bases de datos. **Bajo ninguna circunstancia debes incluir valores reales en los archivos `.env.example` ni hacer commits de archivos `.env`.**

## 2. Configuración en la Raíz / Backend

En la raíz del proyecto existe un archivo `.env.example`. Debes copiarlo, renombrarlo a `.env` y llenarlo con los datos requeridos. Los microservicios administrados por Docker Compose consumen este archivo global.

Variables comunes esperadas:
- `DATABASE_URL`: Cadena de conexión a PostgreSQL.
- `JWT_SECRET_KEY`: Clave para la firma de tokens JWT.
- `GOOGLE_CLIENT_ID`: Identificador para autenticación con Google.
- `FRONTEND_URL`: URL base del frontend para permitir CORS.

Adicionalmente, cada microservicio puede requerir variables específicas, las cuales están documentadas en su respectivo `README.md` dentro de `backend/servicios/`.

## 3. Configuración en el Frontend

La carpeta `frontend/` también contiene sus propios archivos de ejemplo: `.env.example`. Copia este archivo a `.env.development` y `.env.production` según necesites.

Variables del frontend típicas:
- `VITE_API_BASE_URL`: La URL base de la Puerta de Enlace (ej. `http://localhost:5000` en desarrollo).
- `VITE_GOOGLE_CLIENT_ID`: El Client ID de Google para inicializar el botón de OAuth.

## 4. Gestión en producción

En un entorno productivo como AWS Elastic Beanstalk o Amazon ECS, las variables de entorno se inyectan a través del panel de configuración o mediante AWS Secrets Manager. No se suben los archivos `.env` al servidor.
