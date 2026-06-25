# Despliegue en AWS

Descripción corta:
Este documento proporciona una guía paso a paso para desplegar el frontend y los microservicios de backend de PsicoConecta utilizando los servicios de Amazon Web Services (AWS) como Elastic Beanstalk, S3 y CloudFront.

## 1. Requisitos previos

- Cuenta AWS activa (la capa gratuita o free tier es suficiente para el entorno de desarrollo).
- Repositorio del proyecto clonado y dependencias instaladas.

## 2. Backend — Elastic Beanstalk (Flask)

### 2.1 Preparar el backend para producción

En `backend/servicios/servicio-usuarios/ejecutar.py` ya está listo. Solo se requiere crear un archivo `Procfile` en la raíz de ese servicio si no existe, para que Elastic Beanstalk (EB) sepa cómo iniciar la aplicación:

**`backend/servicios/servicio-usuarios/Procfile`**
```
web: python ejecutar.py
```

### 2.2 Crear el entorno en AWS Console

1. Abrir **AWS Console** → **Elastic Beanstalk**.
2. Click en **"Crear aplicación"**.
3. Nombre de la aplicación: `psicoconecta-api`.
4. Plataforma: **Python** (última versión compatible).
5. Código fuente: **Subir** el archivo `.zip` con el contenido de `backend/servicios/servicio-usuarios/` (excluyendo entornos virtuales `venv`, carpetas `__pycache__` y archivos `.env`).
6. Click en **"Crear entorno"**.

> [!NOTE]
> La creación del entorno de EB puede tomar entre 5 y 10 minutos.

### 2.3 Configurar variables de entorno

En el menú de EB: **Configuración** → **Software** → **Propiedades del entorno**, agregar:

*   `PORT`: `5001`
*   `MODO_DESARROLLO`: `false`
*   `SECRET_KEY`: (clave generada aleatoriamente)
*   `JWT_SECRET_KEY`: (clave generada aleatoriamente)
*   `FRONTEND_URL`: `https://tudominio.cloudfront.net`
*   `DATABASE_URL`: URL de conexión si se usa RDS o dejar vacío para usar SQLite (solo pruebas).
*   *(Otras variables de Google OAuth definidas en `variables-entorno.md`)*

## 3. Frontend — S3 y CloudFront

### 3.1 Construir el frontend

```powershell
cd frontend
npm install
npm run build
```
Se generará la carpeta `frontend/dist/`.

### 3.2 Crear bucket S3

1. AWS Console → **S3** → **"Crear bucket"**.
2. Nombre: `psicoconecta-frontend-unl` (debe ser globalmente único).
3. **Desmarcar** la opción de "Bloquear todo el acceso público".
4. Crear bucket.

### 3.3 Subir archivos y configurar políticas

Subir el contenido de `frontend/dist/` a la raíz del bucket S3 y configurar el bucket para **Alojamiento de sitios web estáticos** (con `index.html` como documento de índice y error). Aplicar la siguiente política de permisos públicos (reemplazando el nombre del bucket):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::<nombre-del-bucket>/*"
    }
  ]
}
```

### 3.4 Distribución de CloudFront

1. AWS Console → **CloudFront** → **"Crear distribución"**.
2. Origen: Seleccionar el bucket S3 recién creado.
3. Política del visor (Viewer protocol policy): **Redirect HTTP to HTTPS**.
4. Objeto raíz predeterminado: `index.html`.
5. Páginas de error: Configurar respuesta 200 con ruta `/index.html` para errores 403 y 404 (necesario para el enrutamiento de la SPA en React).

## 4. Base de datos — RDS PostgreSQL (Opcional)

Si no se desea utilizar SQLite, se debe crear una instancia RDS:
1. AWS Console → **RDS** → **"Crear base de datos"**.
2. Motor: PostgreSQL. Capa gratuita (`db.t4g.micro`).
3. Actualizar la variable `DATABASE_URL` en Elastic Beanstalk apuntando al endpoint de esta nueva base de datos.
