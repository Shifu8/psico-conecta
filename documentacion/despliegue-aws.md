# Despliegue en AWS Console

> Para la parte de monitoreo de infraestructura y auditoria SaaS, revisa tambien
> `documentacion/monitoreo-aws-cloudwatch.md`.

## Requisitos previos

- Cuenta AWS (free tier suficiente para desarrollo)
- Proyecto subido a GitHub

---

## 1. Backend — Elastic Beanstalk (Flask)

### 1.1 Preparar el backend para producción

En `backend/servicios/servicio-usuarios/ejecutar.py` ya está listo. Solo crear
un `Procfile` en la raíz del backend para que EB sepa cómo iniciar:

**`backend/servicios/servicio-usuarios/Procfile`**
```
web: python ejecutar.py
```

### 1.2 Crear el entorno en AWS Console

1. Abrir **AWS Console** → **Elastic Beanstalk**
2. Click **"Crear aplicación"**
3. Nombre: `psicoconecta-api`
4. Plataforma: **Python** (última versión)
5. Código fuente: **Subir** el zip de `backend/servicios/servicio-usuarios/`
   (sin venv, sin `__pycache__`, sin `.env`)
6. Click **"Crear entorno"**

> ⏳ Esperar 5–10 min hasta que el entorno esté verde (OK).

### 1.3 Configurar variables de entorno

En el menú **Configuración** → **Software** → **Propiedades del entorno**:

| Clave | Valor |
|-------|-------|
| `PORT` | `5001` |
| `MODO_DESARROLLO` | `false` |
| `SECRET_KEY` | (generar una segura) |
| `JWT_SECRET_KEY` | (generar otra) |
| `GOOGLE_CLIENT_ID` | `339658076678-8b46grlhh639h3ujsp1fe05bkbqlvnqo.apps.googleusercontent.com` |
| `GOOGLE_LOGIN_CLIENT_ID` | `339658076678-kah0e205d5asf6ufnlh009lh5i4g8u70.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | (el secreto del cliente desktop) |
| `GOOGLE_REFRESH_TOKEN` | (el refresh token de Gmail) |
| `GOOGLE_SENDER_EMAIL` | `brandon.medina@unl.edu.ec` |
| `FRONTEND_URL` | `https://tudominio.cloudfront.net` |
| `DATABASE_URL` | (dejar vacío para SQLite o poner RDS) |
| `COGNITO_ENABLED` | `false` |

### 1.4 Health check

EB usa `http://<url>/health` automáticamente (el endpoint ya existe).

### 1.5 Seed de datos

Conectarse por SSH a la instancia EB y ejecutar:

```bash
cd /var/app/current
python datos_iniciales.py
```

---

## 2. Frontend — S3 + CloudFront

### 2.1 Construir el frontend

```powershell
cd frontend
npm install
npm run build
```

Se genera la carpeta `frontend/dist/`.

### 2.2 Crear bucket S3

1. AWS Console → **S3** → **"Crear bucket"**
2. Nombre: `psicoconecta-frontend` (único global)
3. Región: misma que el backend
4. **Desmarcar** "Bloquear todo el acceso público"
5. Click **"Crear bucket"**

### 2.3 Subir archivos

```powershell
aws s3 sync frontend/dist/ s3://psicoconecta-frontend/
```

O desde la consola: **Subir** todos los archivos de `frontend/dist/`.

### 2.4 Configurar sitio estático

1. Ir al bucket → **Propiedades** → **Alojamiento de sitios web estáticos**
2. Habilitar
3. Índice: `index.html`
4. Error: `index.html`
5. Guardar

### 2.5 Política de bucket

En **Permisos** → **Política del bucket**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::psicoconecta-frontend/*"
    }
  ]
}
```

### 2.6 CloudFront (opcional, recomendado)

1. AWS Console → **CloudFront** → **"Crear distribución"**
2. Origen: el bucket S3 `psicoconecta-frontend`
3. **Origin Access Control** (OAC): crear nuevo, `Sign requests`
4. Viewer protocol policy: **Redirect HTTP to HTTPS**
5. Default root object: `index.html`
6. Error pages: crear error 403 → response page `/index.html`, code 200

### 2.7 Actualizar URL en frontend

En el bucket S3 (o CloudFront), copiar la URL del sitio.
En el backend EB → Config → Environment properties:

```
FRONTEND_URL=https://<url-cloudfront>.cloudfront.net
```

### 2.8 Google OAuth — autorizar origen

En Google Cloud Console → APIs & Services → Credentials:

- **Web client** (`...8u70`): agregar en **Authorized JavaScript origins**:
  - `https://<tu-bucket>.s3-website-<region>.amazonaws.com`
  - `https://<url-cloudfront>.cloudfront.net`

---

## 3. Base de datos — RDS PostgreSQL (opcional)

1. AWS Console → **RDS** → **"Crear base de datos"**
2. PostgreSQL, Free tier (`db.t4g.micro`)
3. Nombre: `psicoconecta`
4. Usuario/contraseña: guardarlos
5. Crear

En el backend EB → Config → Environment properties:

| Clave | Valor |
|-------|-------|
| `DATABASE_URL` | `postgresql://usuario:pass@<rds-endpoint>:5432/psicoconecta` |
| `DATABASE_SCHEMA` | `usuarios_schema` |

---

## 4. Verificar despliegue

1. Abrir la URL del frontend (S3 o CloudFront)
2. Debería cargar la landing page de PsicoConecta
3. Click "Iniciar sesión" → probar login con demo
4. Probar recuperación de contraseña

---

## Resumen de URLs

| Componente | URL |
|------------|-----|
| Frontend | `https://<url-cloudfront>.cloudfront.net` |
| Backend API | `http://<eb-url>.elasticbeanstalk.com` |
| Health check | `http://<eb-url>.elasticbeanstalk.com/health` |

---

## Costos estimados (free tier)

| Servicio | Free tier |
|----------|-----------|
| Elastic Beanstalk (EC2 t2.micro) | 750 h/mes gratis |
| S3 | 5 GB gratis |
| CloudFront | 1 TB gratis |
| RDS (db.t4g.micro) | 750 h/mes gratis |
