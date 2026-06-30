# PsicoConecta

PsicoConecta es una plataforma para conectar pacientes y profesionales de psicologia. El proyecto esta organizado como un monorepo con frontend React y backend Flask. El servicio de usuarios esta funcional; los modulos de citas, teleconsulta, pagos e inteligencia IoT quedan como bases preparadas para evolucionar.

## Tecnologias

| Area | Tecnologia |
| --- | --- |
| Frontend | React + Vite + TailwindCSS + Framer Motion |
| Backend | Python Flask |
| Autenticacion | JWT local + Google OAuth directo |
| Recuperacion de contrasena | Gmail API, sin SMTP |
| Base relacional | SQLite local o PostgreSQL |
| CAPTCHA | Cloudflare Turnstile opcional |
| Cloud | AWS, CloudFront, ECS, S3 |

No se usa Node.js como backend, Gmail SMTP, MongoDB, Jitsi ni pagos reales.

## Requisitos para ejecutar

Instala primero:

- Git: https://git-scm.com/downloads
- Python 3.11 o superior: https://www.python.org/downloads/
- Node.js 20 LTS o superior, incluye npm: https://nodejs.org/
- Docker Desktop, opcional, solo si quieres usar PostgreSQL con Docker: https://www.docker.com/products/docker-desktop/

Comprueba que quedaron instalados:

```powershell
git --version
python --version
node --version
npm --version
```

En Windows PowerShell, si `npm run dev` falla por politicas de ejecucion, usa `npm.cmd run dev`. No necesitas cambiar `Set-ExecutionPolicy`.

## Descargar el proyecto

```powershell
git clone https://github.com/Shifu8/psico-conecta.git
cd psico-conecta
```

Si descargaste el ZIP desde GitHub, descomprimelo y entra a la carpeta raiz del proyecto.

## Inicio rapido local

Para desarrollo local se recomienda usar SQLite. Asi no necesitas instalar PostgreSQL ni Docker para probar login, registro y paneles.

### 1. Backend

Abre una terminal en la raiz del proyecto y ejecuta:

```powershell
cd backend\servicios\servicio-usuarios
copy .env.example .env
```

Edita `.env` y deja estas lineas asi para usar SQLite local:

```env
DATABASE_URL=sqlite:///datos_local.db
DATABASE_SCHEMA=
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
```

Luego instala dependencias, carga datos demo y arranca Flask:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe datos_iniciales.py
.\venv\Scripts\python.exe ejecutar.py
```

Deja esta terminal abierta. El backend queda en:

```text
http://127.0.0.1:5001
```

Para siguientes ejecuciones solo necesitas:

```powershell
cd backend\servicios\servicio-usuarios
.\venv\Scripts\python.exe ejecutar.py
```

Si quieres reiniciar la base local, borra el archivo SQLite y vuelve a ejecutar el seed:

```powershell
Remove-Item .\instance\datos_local.db -ErrorAction SilentlyContinue
.\venv\Scripts\python.exe datos_iniciales.py
.\venv\Scripts\python.exe ejecutar.py
```

### 2. Frontend

Abre otra terminal en la raiz del proyecto:

```powershell
cd frontend
npm install
npm run dev
```

Si PowerShell bloquea `npm`, usa:

```powershell
npm.cmd install
npm.cmd run dev
```

Abre la app en:

```text
http://localhost:5173
```

Para siguientes ejecuciones solo necesitas:

```powershell
cd frontend
npm run dev
```

## Variables opcionales

### Cloudflare Turnstile

Turnstile protege registro, inicio de sesion y recuperacion de contrasena. Es opcional en desarrollo.

Para activarlo configura:

Backend `backend/servicios/servicio-usuarios/.env`:

```env
TURNSTILE_SECRET_KEY=<secret-key-de-cloudflare>
```

Frontend `frontend/.env.development`:

```env
VITE_TURNSTILE_SITE_KEY=<site-key-de-cloudflare>
```

El widget debe permitir `localhost` y `127.0.0.1` en Cloudflare. Si estas variables quedan vacias, la app puede correr localmente sin CAPTCHA.

### Google Login

Para usar inicio de sesion con Google configura el mismo cliente web en ambos lados:

Backend `.env`:

```env
GOOGLE_LOGIN_CLIENT_ID=<web-client-id>
```

Frontend `frontend/.env.development`:

```env
VITE_GOOGLE_CLIENT_ID=<web-client-id>
```

### Recuperacion con Gmail API

La recuperacion de contrasena usa Gmail API. Para envio real configura:

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
GOOGLE_SENDER_EMAIL=
SES_ENABLED=false
SES_REGION=us-east-2
SES_SENDER_EMAIL=
FRONTEND_URL=http://localhost:5173
```

En modo desarrollo, si no hay credenciales de Gmail, el backend puede devolver el token de recuperacion para pruebas locales.
Si Gmail devuelve `invalid_grant`, el refresh token ya no es valido y debe
renovarse con `backend/servicios/servicio-usuarios/setup_google_credentials.py`
antes de sincronizar secretos en AWS.

## Credenciales de demostracion

Despues de ejecutar `datos_iniciales.py`, puedes entrar con:

| Rol | Correo | Contrasena |
| --- | --- | --- |
| ADMIN | `admin@psicoconecta.com` | `Admin123*` |
| PSYCHOLOGIST | `psicologo@psicoconecta.com` | `Psicologo123*` |
| PSYCHOLOGIST | `laura@psicoconecta.com` | `Psicologo123*` |
| PATIENT | `paciente@psicoconecta.com` | `Paciente123*` |

Estas cuentas son solo para desarrollo local.

## PostgreSQL con Docker opcional

Si quieres trabajar con PostgreSQL:

```powershell
docker compose up -d postgres
```

Docker crea la base `psicoconecta` y los esquemas:

- `usuarios_schema`
- `citas_schema`
- `teleconsulta_schema`
- `pagos_schema`

Luego en `backend/servicios/servicio-usuarios/.env` usa:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/psicoconecta
DATABASE_SCHEMA=usuarios_schema
```

Para levantar tambien pgAdmin:

```powershell
docker compose --profile tools up -d
```

## Scripts opcionales

El proyecto incluye scripts para Windows:

```powershell
.\scripts\local-backend.ps1
.\scripts\local-frontend.ps1
```

No son obligatorios. Los comandos manuales de las secciones anteriores son la forma mas clara para nuevos colaboradores.

## Pruebas y build

Backend, desde `backend/servicios/servicio-usuarios`:

```powershell
.\venv\Scripts\python.exe -m pytest
```

Frontend, desde `frontend`:

```powershell
npm run build
```

Si PowerShell bloquea npm:

```powershell
npm.cmd run build
```

## Arquitectura

| Componente | Puerto | Estado |
| --- | ---: | --- |
| Frontend React | 5173 | Funcional, responsive, modo claro y oscuro |
| Puerta de enlace API | 5000 | Descubrimiento base |
| Servicio de usuarios | 5001 | Funcional |
| Servicio de citas | 5002 | Base preparada |
| Servicio de teleconsulta | 5003 | Base preparada |
| Servicio de pagos | 5004 | Base preparada |
| Servicio de inteligencia e IoT | 5005 | Base preparada |
| PostgreSQL | 5432 | Opcional con Docker |
| pgAdmin | 5050 | Opcional con perfil Docker `tools` |

## Estructura principal

```text
psico-conecta/
|-- backend/
|   |-- compartido/
|   |-- puerta-enlace-api/
|   |-- servicios/
|   |   |-- servicio-citas/
|   |   |-- servicio-inteligencia-iot/
|   |   |-- servicio-pagos/
|   |   |-- servicio-teleconsulta/
|   |   `-- servicio-usuarios/
|   `-- requirements-comunes.txt
|-- documentacion/
|-- frontend/
|   `-- src/
|-- infraestructura/
|-- scripts/
|-- docker-compose.yml
`-- README.md
```


## Inicio rápido local

### Sin Docker

En una terminal:

```powershell
.\scripts\local-backend.ps1
```

Si SQLite local quedó a medias por un error anterior, reinícialo con:

```powershell
.\scripts\local-backend.ps1 -Reset
```

En otra terminal:

```powershell
.\scripts\local-frontend.ps1
```

Abrir `http://localhost:5173`.

### Opción recomendada: Docker + Vite

Levanta PostgreSQL y el servicio de usuarios. Docker ejecuta el seed antes de
iniciar Flask, por lo que las credenciales demo quedan listas.

```powershell
docker compose up servicio-usuarios
```

En otra terminal:

```powershell
cd frontend
npm install
npm run dev
```

Abrir `http://localhost:5173`.

El frontend local usa `frontend/.env.development`, que apunta a
`http://127.0.0.1:5001`. La build de producción en GitHub obtiene el DNS del
ALB `psicoconecta-alb` y usa ese valor como `VITE_API_URL`.

### Opción manual: PostgreSQL + Flask

La demostración local requiere PostgreSQL. Copia `backend/servicios/servicio-usuarios/.env.example` a `.env` antes de iniciar el servicio.

```powershell
cd backend\servicios\servicio-usuarios
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python datos_iniciales.py
python ejecutar.py
```

### 2. Frontend

En otra terminal:

```powershell
cd frontend
npm install
npm run dev
```

Abrir `http://localhost:5173`.

### 3. PostgreSQL con Docker

Para trabajar con PostgreSQL:

```powershell
docker compose up -d postgres
```

Docker crea automáticamente la base `psicoconecta` y sus cuatro esquemas. Para
incluir pgAdmin:

```powershell
docker compose --profile tools up -d
```

Copiar `backend\servicios\servicio-usuarios\.env.example` como `.env` antes de
iniciar Flask con PostgreSQL.

## Migraciones

Desde `backend\servicios\servicio-usuarios`:

```powershell
flask --app ejecutar.py db init
flask --app ejecutar.py db migrate -m "esquema inicial de usuarios"
flask --app ejecutar.py db upgrade
```

## Credenciales de demostración

| Rol | Correo | Contraseña |
| --- | --- | --- |
| ADMIN | `admin@psicoconecta.com` | `Admin123*` |
| PSYCHOLOGIST | `psicologo@psicoconecta.com` | `Psicologo123*` |
| PSYCHOLOGIST | `laura@psicoconecta.com` | `Psicologo123*` |
| PATIENT | `paciente@psicoconecta.com` | `Paciente123*` |

Estas cuentas existen únicamente para desarrollo local.

## Recuperación con Gmail API

El servicio genera un token temporal seguro, guarda su hash con expiración de
30 minutos y envía un enlace mediante Gmail API. No usa SMTP. En modo local,
sin credenciales, el endpoint devuelve el token para permitir la demostración.

Variables requeridas:

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
GOOGLE_SENDER_EMAIL=
SES_ENABLED=false
SES_REGION=us-east-2
SES_SENDER_EMAIL=
FRONTEND_URL=http://localhost:5173
```

## Inicio de sesión con Google (directo)

El flujo es:

```text
@react-oauth/google (frontend) -> token ID -> Flask (verificación) -> PostgreSQL
```

El frontend usa `@react-oauth/google` y el backend verifica el token ID
contra Google mediante `google-auth` y el endpoint `tokeninfo`.

Variables requeridas:

```env
GOOGLE_LOGIN_CLIENT_ID=<web-client-id>
VITE_GOOGLE_CLIENT_ID=<mismo-client-id>
```

## Producción HTTPS, Gmail y CAPTCHA

Para producción, el frontend debe usar CloudFront como origen seguro:

```env
VITE_API_URL=https://d1wkhs3cq8vcom.cloudfront.net
FRONTEND_URL=https://d1wkhs3cq8vcom.cloudfront.net
CORS_ORIGINS=https://d1wkhs3cq8vcom.cloudfront.net,http://psicoconecta-frontend-060899556466.s3-website.us-east-2.amazonaws.com
```

La recuperación de contraseña necesita que ECS reciba `GOOGLE_CLIENT_ID`,
`GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` y `GOOGLE_SENDER_EMAIL` desde
Secrets Manager. El script `infraestructura/aws/actualizar-secretos-usuarios.ps1`
lee esos valores desde `backend/servicios/servicio-usuarios/.env` y los actualiza
en AWS.

CAPTCHA usa Cloudflare Turnstile de forma opcional. Si configuras
`VITE_TURNSTILE_SITE_KEY` en el frontend y `TURNSTILE_SECRET_KEY` en el backend,
los formularios de registro, inicio de sesión y recuperación validan el desafío.


## Endpoints principales

Autenticacion:

- `POST /api/usuarios/autenticacion/registro`
- `POST /api/usuarios/autenticacion/inicio-sesion`
- `POST /api/usuarios/autenticacion/cierre-sesion`
- `POST /api/usuarios/autenticacion/recuperar-contrasena`
- `POST /api/usuarios/autenticacion/restablecer-contrasena`
- `GET /api/usuarios/autenticacion/mi-perfil`
- `POST /api/usuarios/autenticacion/google`
- `GET /api/usuarios/autenticacion/google/configuracion`

Administracion:

- `GET /api/usuarios`
- `GET /api/usuarios/<id>`
- `PUT /api/usuarios/<id>`
- `DELETE /api/usuarios/<id>`
- `PATCH /api/usuarios/<id>/status`
- `GET|POST /api/usuarios/roles`
- `PUT|DELETE /api/usuarios/roles/<id>`

Modulos preparados:

- `GET|POST /api/citas`
- `POST /api/teleconsulta/zoom/crear-reunion`
- `GET /api/teleconsulta/sesiones`
- `POST /api/pagos/crear-pago`
- `GET /api/pagos`
- `GET|POST /api/iot/emociones`
- `GET|POST /api/iot/lecturas`

## Documentacion

- [Arquitectura](documentacion/arquitectura.md)
- [Arbol completo del proyecto](documentacion/arbol-del-proyecto.txt)
- [Decisiones tecnicas](documentacion/decisiones-tecnicas.md)
- [Diseno de datos](documentacion/diseno-de-datos.md)
- [Requisitos funcionales](documentacion/requisitos-funcionales.md)
- [Requisitos no funcionales](documentacion/requisitos-no-funcionales.md)
- [Despliegue AWS](documentacion/despliegue-aws.md)

## Despliegue desde GitHub

El workflow `.github/workflows/deploy.yml` se ejecuta al hacer push a `main`.

Para desplegar en AWS necesita estos secrets en GitHub:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCOUNT_ID`
- `VITE_GOOGLE_CLIENT_ID`, opcional
- `VITE_TURNSTILE_SITE_KEY`, opcional
- `TURNSTILE_SECRET_KEY`, opcional

Si no existen las credenciales AWS, el workflow omite el deploy y termina correctamente. Asi el repositorio puede usarse para desarrollo local sin configurar AWS.

## Produccion

Antes de publicar configura secretos fuera del repositorio, HTTPS, infraestructura como codigo, CI/CD, monitoreo, backups, politicas IAM de minimo privilegio y pruebas de carga. No subas `.env`, archivos OAuth, certificados ni credenciales reales.
