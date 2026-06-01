# PsicoConecta

PsicoConecta es una plataforma cloud para conectar pacientes y profesionales de
psicología. El repositorio está organizado como un monorepo de microservicios:
la gestión de usuarios está implementada y los módulos de citas, teleconsulta,
pagos e inteligencia IoT tienen una base Flask preparada para su evolución.

## Tecnologías definitivas

| Área | Tecnología |
| --- | --- |
| Frontend | React + Vite + TailwindCSS + Framer Motion |
| Backend | Python Flask |
| Autenticación | JWT local + Google OAuth directo |
| Recuperación de contraseña | Gmail API (sin SMTP) |
| Inicio de sesión con Google | Directo desde Flask (@react-oauth/google) |
| Base relacional | PostgreSQL con esquemas separados |
| IoT y datos flexibles | DynamoDB |
| Teleconsulta | Zoom API |
| Pagos | Stripe Sandbox |
| Almacenamiento | Amazon S3 |
| Cloud | AWS |

No se usa Node.js como backend, Gmail SMTP, MongoDB, Jitsi ni pagos reales.

## Arquitectura

| Componente | Puerto | Estado |
| --- | ---: | --- |
| Frontend React | 5173 | Funcional, responsive, modo claro y oscuro |
| Puerta de enlace API | 5000 | Descubrimiento base |
| Servicio de usuarios | 5001 | Funcional |
| Servicio de citas | 5002 | Estructura avanzada preparada |
| Servicio de teleconsulta | 5003 | Zoom API preparado |
| Servicio de pagos | 5004 | Stripe Sandbox preparado |
| Servicio de inteligencia e IoT | 5005 | DynamoDB y AWS IoT Core preparados |
| PostgreSQL | 5432 | Una instancia con cuatro esquemas |
| pgAdmin opcional | 5050 | Perfil Docker `tools` |

PostgreSQL usa una sola instancia para optimizar costos académicos:

- `usuarios_schema`
- `citas_schema`
- `teleconsulta_schema`
- `pagos_schema`

DynamoDB usa las tablas `emociones`, `lecturas_iot`, `notificaciones` y
`logs_iot`.

## Alcance de seguridad actual

El frontend y el servicio de usuarios incluyen validación de entradas,
autenticación JWT, control de acceso por rol y límite de intentos de inicio de
sesión. Los servicios de citas, teleconsulta, pagos e inteligencia IoT siguen
siendo esqueletos locales en memoria: no deben exponerse públicamente hasta
implementar persistencia, autenticación y autorización por propietario.

## Estructura principal

```text
PsicoConecta-main/
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
|       |-- componentes/
|       |-- contexto/
|       |-- paginas/
|       |-- plantillas/
|       |-- rutas/
|       `-- servicios/
|-- infraestructura/
|   `-- postgres/
|-- docker-compose.yml
`-- README.md
```

## Inicio rápido local

### 1. Servicio de usuarios

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

## Endpoints principales

Autenticación:

- `POST /api/usuarios/autenticacion/registro`
- `POST /api/usuarios/autenticacion/inicio-sesion`
- `POST /api/usuarios/autenticacion/cierre-sesion`
- `POST /api/usuarios/autenticacion/recuperar-contrasena`
- `POST /api/usuarios/autenticacion/restablecer-contrasena`
- `GET /api/usuarios/autenticacion/mi-perfil`
- `POST /api/usuarios/autenticacion/google`
- `GET /api/usuarios/autenticacion/google/configuracion`

Administración:

- `GET /api/usuarios`
- `GET /api/usuarios/<id>`
- `PUT /api/usuarios/<id>`
- `DELETE /api/usuarios/<id>`
- `PATCH /api/usuarios/<id>/status`
- `GET|POST /api/usuarios/roles`
- `PUT|DELETE /api/usuarios/roles/<id>`

Módulos preparados:

- `GET|POST /api/citas`
- `POST /api/teleconsulta/zoom/crear-reunion`
- `GET /api/teleconsulta/sesiones`
- `POST /api/pagos/crear-pago`
- `GET /api/pagos`
- `GET|POST /api/iot/emociones`
- `GET|POST /api/iot/lecturas`

## Documentación

- [Arquitectura](documentacion/arquitectura.md)
- [Árbol completo del proyecto](documentacion/arbol-del-proyecto.txt)
- [Decisiones técnicas](documentacion/decisiones-tecnicas.md)
- [Diseño de datos](documentacion/diseno-de-datos.md)
- [Requisitos funcionales](documentacion/requisitos-funcionales.md)
- [Requisitos no funcionales](documentacion/requisitos-no-funcionales.md)
- [Despliegue AWS](documentacion/despliegue-aws.md)

## Producción

Antes de publicar se deben configurar secretos fuera del repositorio, HTTPS,
infraestructura como código, CI/CD, monitoreo, backups, políticas IAM de mínimo
privilegio y pruebas de carga. No subir `.env`, archivos OAuth, certificados ni
credenciales reales.
