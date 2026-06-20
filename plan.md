# Plan de Implementación — Módulo de Gestión de Citas
**Proyecto:** PsicoConecta  
**Servicio:** `servicio-citas` — Puerto `5002`  
**Stack:** Flask (Python) · PostgreSQL (`citas_schema`) · React + Vite · TailwindCSS · Framer Motion  

---

## Índice

1. [Visión General](#1-visión-general)
2. [Modelado de Base de Datos](#2-modelado-de-base-de-datos)
3. [Backend — Servicio de Citas (Flask)](#3-backend--servicio-de-citas-flask)
4. [API Gateway — Enrutamiento](#4-api-gateway--enrutamiento)
5. [Frontend — Componentes React](#5-frontend--componentes-react)
6. [Lógica de Negocio y Reglas](#6-lógica-de-negocio-y-reglas)
7. [Seguridad y Autorización](#7-seguridad-y-autorización)
8. [Integración con Otros Servicios](#8-integración-con-otros-servicios)
9. [Orden de Implementación (Sprints)](#9-orden-de-implementación-sprints)
10. [Estructura de Archivos Propuesta](#10-estructura-de-archivos-propuesta)
11. [Docker y Variables de Entorno](#11-docker-y-variables-de-entorno)
12. [Pruebas](#12-pruebas)

---

## 1. Visión General

El módulo de citas permite a **Pacientes** agendar, reprogramar y cancelar sesiones con **Psicólogos**, mientras que los Psicólogos configuran su disponibilidad y confirman o rechazan solicitudes. Los **Administradores** tienen visibilidad total y control de todas las citas de la plataforma.

### Flujo General

```
Paciente ve disponibilidad → Selecciona horario → Agenda cita (PENDIENTE)
    → Psicólogo confirma/rechaza → Cita (CONFIRMADA / CANCELADA)
    → (Opcional) Psicólogo o Paciente reprograman → Cita (REPROGRAMADA)
    → Cita ocurre → Estado final (COMPLETADA)
```

### Estados de una Cita

| Estado       | Descripción                                              |
|--------------|----------------------------------------------------------|
| `PENDIENTE`  | Creada por el paciente, esperando confirmación           |
| `CONFIRMADA` | Aceptada por el psicólogo                                |
| `REPROGRAMADA` | Fecha/hora modificada, requiere reconfirmación         |
| `CANCELADA`  | Cancelada por paciente, psicólogo o admin                |
| `COMPLETADA` | La sesión ya ocurrió                                     |
| `NO_ASISTIDA`| El paciente no se presentó                               |

---

## 2. Modelado de Base de Datos

Todas las tablas viven dentro del esquema `citas_schema` en la instancia PostgreSQL compartida.

### 2.1 Tabla `disponibilidad`

Define los bloques horarios semanales en los que un psicólogo puede atender.

```sql
CREATE TABLE citas_schema.disponibilidad (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    psicologo_id    UUID NOT NULL,          -- FK lógica al users_schema
    dia_semana      SMALLINT NOT NULL,       -- 0=Lunes … 6=Domingo
    hora_inicio     TIME NOT NULL,
    hora_fin        TIME NOT NULL,
    duracion_slot   SMALLINT DEFAULT 50,     -- minutos por sesión
    activo          BOOLEAN DEFAULT TRUE,
    fecha_creacion  TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_hora CHECK (hora_fin > hora_inicio),
    CONSTRAINT uq_disp UNIQUE (psicologo_id, dia_semana, hora_inicio)
);
```

### 2.2 Tabla `excepciones_disponibilidad`

Días bloqueados (vacaciones, feriados, ausencias puntuales).

```sql
CREATE TABLE citas_schema.excepciones_disponibilidad (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    psicologo_id    UUID NOT NULL,
    fecha           DATE NOT NULL,
    motivo          VARCHAR(255),
    fecha_creacion  TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_excepcion UNIQUE (psicologo_id, fecha)
);
```

### 2.3 Tabla `citas`

Registro central de cada sesión.

```sql
CREATE TABLE citas_schema.citas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id     UUID NOT NULL,           -- FK lógica al users_schema
    psicologo_id    UUID NOT NULL,           -- FK lógica al users_schema
    fecha_hora_inicio   TIMESTAMPTZ NOT NULL,
    fecha_hora_fin      TIMESTAMPTZ NOT NULL,
    estado          VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    modalidad       VARCHAR(15) DEFAULT 'VIRTUAL',   -- VIRTUAL | PRESENCIAL
    motivo_consulta TEXT,
    notas_psicologo TEXT,
    motivo_cancelacion  TEXT,
    cancelado_por   UUID,                    -- quien canceló
    reprogramada_desde  UUID REFERENCES citas_schema.citas(id),
    fecha_creacion  TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_estado CHECK (
        estado IN ('PENDIENTE','CONFIRMADA','REPROGRAMADA','CANCELADA','COMPLETADA','NO_ASISTIDA')
    ),
    CONSTRAINT chk_modalidad CHECK (modalidad IN ('VIRTUAL','PRESENCIAL')),
    CONSTRAINT chk_horas_cita CHECK (fecha_hora_fin > fecha_hora_inicio)
);

CREATE INDEX idx_citas_paciente   ON citas_schema.citas(paciente_id);
CREATE INDEX idx_citas_psicologo  ON citas_schema.citas(psicologo_id);
CREATE INDEX idx_citas_fecha      ON citas_schema.citas(fecha_hora_inicio);
CREATE INDEX idx_citas_estado     ON citas_schema.citas(estado);
```

### 2.4 Tabla `historial_cambios_citas`

Auditoría de cada cambio de estado.

```sql
CREATE TABLE citas_schema.historial_cambios_citas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cita_id         UUID NOT NULL REFERENCES citas_schema.citas(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(20),
    estado_nuevo    VARCHAR(20) NOT NULL,
    cambiado_por    UUID NOT NULL,           -- usuario que realizó el cambio
    motivo          TEXT,
    fecha_cambio    TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 3. Backend — Servicio de Citas (Flask)

### 3.1 Dependencias a instalar

```
flask
flask-sqlalchemy
flask-migrate
psycopg2-binary
flask-jwt-extended
marshmallow
python-dotenv
pytz
```

Agregar al `requirements.txt` de `servicio-citas`. Las dependencias que ya existan en `backend/requirements-comunes.txt` (compartido entre todos los servicios) no necesitan duplicarse; solo agregar las que sean exclusivas de este servicio.

### 3.2 Estructura del módulo Flask

Seguir la misma convención de nombres que `servicio-usuarios`.

```
backend/servicios/servicio-citas/
├── app/
│   ├── __init__.py          # Factory de Flask, inicializa db, jwt y migrate
│   ├── config.py            # Configuración por entorno
│   ├── modelos/
│   │   ├── __init__.py
│   │   ├── cita.py
│   │   ├── disponibilidad.py
│   │   └── historial.py
│   ├── esquemas/            # Marshmallow — validación y serialización
│   │   ├── esquema_cita.py
│   │   └── esquema_disponibilidad.py
│   ├── servicios/           # Lógica de negocio pura
│   │   ├── servicio_cita.py
│   │   └── servicio_disponibilidad.py
│   ├── rutas/
│   │   ├── __init__.py
│   │   ├── rutas_citas.py
│   │   └── rutas_disponibilidad.py
│   └── utilidades/
│       ├── autenticacion.py  # Decoradores JWT y roles
│       └── helpers.py        # Generación de slots, validaciones de fecha
├── migrations/              # Generado por Flask-Migrate (flask db init)
├── tests/
├── datos_iniciales.py       # Seed de datos demo (igual que en servicio-usuarios)
├── .env.example             # Plantilla de variables de entorno
├── Dockerfile
├── requirements.txt
└── ejecutar.py              # Punto de entrada Flask (igual que servicio-usuarios)
```

### 3.3 Endpoints de la API

#### Disponibilidad del Psicólogo

| Método | Ruta                                        | Roles               | Descripción                          |
|--------|---------------------------------------------|---------------------|--------------------------------------|
| GET    | `/disponibilidad/<psicologo_id>`            | Todos               | Obtener bloques semanales            |
| POST   | `/disponibilidad`                           | Psicólogo           | Crear un bloque de disponibilidad    |
| PUT    | `/disponibilidad/<id>`                      | Psicólogo           | Editar un bloque                     |
| DELETE | `/disponibilidad/<id>`                      | Psicólogo           | Eliminar un bloque                   |
| GET    | `/disponibilidad/<psicologo_id>/slots`      | Paciente, Admin     | Obtener slots libres para una fecha  |
| POST   | `/disponibilidad/excepciones`               | Psicólogo           | Bloquear un día específico           |
| DELETE | `/disponibilidad/excepciones/<id>`          | Psicólogo           | Desbloquear un día                   |

**Parámetros de `/slots`:**  
`?fecha=YYYY-MM-DD` — Retorna la lista de horarios disponibles (no ocupados) para esa fecha.

---

#### Gestión de Citas

| Método | Ruta                          | Roles                        | Descripción                          |
|--------|-------------------------------|------------------------------|--------------------------------------|
| POST   | `/citas`                      | Paciente                     | Agendar nueva cita                   |
| GET    | `/citas`                      | Admin                        | Listar todas las citas (con filtros) |
| GET    | `/citas/mis-citas`            | Paciente, Psicólogo          | Listar citas propias                 |
| GET    | `/citas/<id>`                 | Paciente, Psicólogo, Admin   | Detalle de una cita                  |
| PUT    | `/citas/<id>/confirmar`       | Psicólogo                    | Confirmar cita pendiente             |
| PUT    | `/citas/<id>/reprogramar`     | Paciente, Psicólogo          | Solicitar nuevo horario              |
| PUT    | `/citas/<id>/cancelar`        | Paciente, Psicólogo, Admin   | Cancelar con motivo                  |
| PUT    | `/citas/<id>/completar`       | Psicólogo                    | Marcar cita como completada          |
| PUT    | `/citas/<id>/no-asistida`     | Psicólogo                    | Marcar inasistencia                  |
| GET    | `/citas/<id>/historial`       | Psicólogo, Admin             | Ver auditoría de cambios             |

**Filtros comunes en `/citas`:**  
`?estado=CONFIRMADA&psicologo_id=...&desde=YYYY-MM-DD&hasta=YYYY-MM-DD&page=1&per_page=20`

---

### 3.4 Lógica clave en `cita_service.py`

```python
# Pseudocódigo de referencia

def agendar_cita(data, paciente_id):
    # 1. Validar que psicologo_id existe (llamada interna al users-service)
    # 2. Obtener disponibilidad semanal del psicólogo para el día de la fecha
    # 3. Verificar que el slot solicitado está dentro de la disponibilidad
    # 4. Verificar que no hay excepción (día bloqueado)
    # 5. Verificar que no existe otra cita CONFIRMADA o PENDIENTE
    #    que se solape con el horario solicitado
    # 6. Crear la cita con estado PENDIENTE
    # 7. Registrar en historial_cambios_citas
    # 8. Retornar cita creada

def confirmar_cita(cita_id, psicologo_id):
    # 1. Obtener cita — validar que pertenece al psicólogo autenticado
    # 2. Validar que estado actual es PENDIENTE o REPROGRAMADA
    # 3. Cambiar estado a CONFIRMADA
    # 4. Registrar en historial
    # 5. [Futuro] Disparar notificación al paciente

def reprogramar_cita(cita_id, nuevo_horario, solicitante_id, rol):
    # 1. Obtener cita — validar pertenencia según rol
    # 2. Validar que estado es PENDIENTE o CONFIRMADA
    # 3. Verificar disponibilidad del nuevo horario (igual que agendar)
    # 4. Guardar cita actual como referencia (reprogramada_desde)
    # 5. Cambiar estado a REPROGRAMADA
    # 6. Actualizar fecha_hora_inicio y fecha_hora_fin
    # 7. Registrar en historial

def cancelar_cita(cita_id, solicitante_id, motivo, rol):
    # 1. Obtener cita — validar pertenencia
    # 2. Validar que no esté ya CANCELADA o COMPLETADA
    # 3. Aplicar política: paciente solo puede cancelar con X horas de anticipación
    # 4. Cambiar estado a CANCELADA, guardar motivo y cancelado_por
    # 5. Registrar en historial

def get_slots_disponibles(psicologo_id, fecha):
    # 1. Obtener bloques de disponibilidad para el día de la semana de `fecha`
    # 2. Verificar que no es una excepción (día bloqueado)
    # 3. Generar todos los slots (hora_inicio + duracion_slot en loop)
    # 4. Consultar citas PENDIENTES y CONFIRMADAS para ese día/psicólogo
    # 5. Filtrar y retornar solo slots sin solapamiento
```

---

## 4. API Gateway — Enrutamiento

El `puerta-enlace-api` (puerto `5000`) ya incluye un stub base `GET|POST /api/citas` (visible en el README). Hay que **expandir** ese stub para cubrir todas las sub-rutas del módulo:

```python
# En puerta-enlace-api — ampliar las rutas existentes de citas

SERVICIO_CITAS_URL = "http://servicio-citas:5002"

# Ruta base ya existente — mantener y ampliar el proxy
@app.route("/api/citas", methods=["GET", "POST"])
@app.route("/api/citas/<path:subpath>", methods=["GET","POST","PUT","DELETE"])
@app.route("/api/disponibilidad/<path:subpath>", methods=["GET","POST","PUT","DELETE"])
def proxy_citas(subpath=""):
    # Reenviar request con headers JWT intactos al servicio de citas
    ...
```

El JWT firmado en el `servicio-usuarios` debe ser verificado por el `servicio-citas` usando la misma clave secreta (`JWT_SECRET_KEY`), compartida vía variables de entorno.

---

## 5. Frontend — Componentes React

### 5.1 Árbol de páginas y componentes

Respetar la estructura de carpetas existente del proyecto (nombres en español):

```
frontend/src/
├── paginas/
│   └── citas/
│       ├── PaginaCitas.jsx              # Página raíz del módulo
│       ├── PaginaAgendarCita.jsx        # Flujo completo de agendamiento
│       └── PaginaDetalleCita.jsx        # Detalle + acciones según rol
├── componentes/
│   └── citas/
│       ├── CalendarioSemanal.jsx        # Vista de semana con slots
│       ├── CalendarioMensual.jsx        # Vista de mes con indicadores
│       ├── SelectorSlot.jsx             # Selector de horario disponible
│       ├── TarjetaCita.jsx              # Card resumida de una cita
│       ├── ListaCitas.jsx               # Listado con filtros y paginación
│       ├── HistorialCita.jsx            # Timeline de cambios de estado
│       ├── InsigniaEstado.jsx           # Pill de color según estado
│       ├── modales/
│       │   ├── ModalAgendarCita.jsx
│       │   ├── ModalReprogramar.jsx
│       │   ├── ModalCancelar.jsx
│       │   └── ModalConfirmar.jsx
│       └── disponibilidad/
│           ├── GestorDisponibilidad.jsx # Panel del psicólogo
│           ├── BloqueHorario.jsx
│           └── ModalExcepcion.jsx
├── hooks/
│   ├── useCitas.js                      # CRUD de citas, estado global
│   ├── useDisponibilidad.js             # Fetch de slots y disponibilidad
│   └── useCalendario.js                 # Navegación de fechas
├── contexto/
│   └── ContextoCitas.jsx                # Context API para estado compartido (si aplica)
├── rutas/
│   └── rutasCitas.jsx                   # Definición de rutas protegidas por rol
└── servicios/
    └── citasApi.js                      # Llamadas axios al gateway /api/citas
```

### 5.2 Vistas por Rol

#### Paciente

- **`/citas`** → `ListaCitas` con sus citas propias + botón "Agendar nueva"
- **`/citas/agendar`** → Seleccionar psicólogo → Ver `CalendarioSemanal` → Elegir `SlotSelector` → Confirmar formulario
- **`/citas/:id`** → `DetalleCitaPage` con opciones: Cancelar / Reprogramar

#### Psicólogo

- **`/citas`** → `CalendarioSemanal` con sus citas del día/semana + `ListaCitas` con filtros
- **`/citas/disponibilidad`** → `GestorDisponibilidad` para gestionar horarios y excepciones
- **`/citas/:id`** → Confirmar / Reprogramar / Marcar Completada / Marcar No Asistida

#### Administrador

- **`/admin/citas`** → `ListaCitas` global con filtros por psicólogo, estado, rango de fechas
- **`/admin/citas/:id`** → Vista completa + opción de cancelar cualquier cita

### 5.3 Servicio de API en el frontend

```javascript
// src/servicios/citasApi.js
import axios from 'axios';

// En desarrollo: VITE_CITAS_API_URL=http://127.0.0.1:5002 (frontend/.env.development)
// En producción: VITE_CITAS_API_URL apunta al gateway vía CloudFront
const API = axios.create({ baseURL: import.meta.env.VITE_CITAS_API_URL });

// Interceptor para inyectar JWT automáticamente
API.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const citasApi = {
  // Disponibilidad
  getSlots:         (psicologoId, fecha) => API.get(`/disponibilidad/${psicologoId}/slots`, { params: { fecha } }),
  getDisponibilidad:(psicologoId)        => API.get(`/disponibilidad/${psicologoId}`),
  crearBloque:      (data)               => API.post('/disponibilidad', data),
  editarBloque:     (id, data)           => API.put(`/disponibilidad/${id}`, data),
  eliminarBloque:   (id)                 => API.delete(`/disponibilidad/${id}`),
  crearExcepcion:   (data)               => API.post('/disponibilidad/excepciones', data),
  eliminarExcepcion:(id)                 => API.delete(`/disponibilidad/excepciones/${id}`),

  // Citas
  agendar:          (data)               => API.post('/citas', data),
  getMisCitas:      (params)             => API.get('/citas/mis-citas', { params }),
  getTodasLasCitas: (params)             => API.get('/citas', { params }),
  getDetalle:       (id)                 => API.get(`/citas/${id}`),
  confirmar:        (id)                 => API.put(`/citas/${id}/confirmar`),
  reprogramar:      (id, data)           => API.put(`/citas/${id}/reprogramar`, data),
  cancelar:         (id, data)           => API.put(`/citas/${id}/cancelar`, data),
  completar:        (id)                 => API.put(`/citas/${id}/completar`),
  marcarNoAsistida: (id)                 => API.put(`/citas/${id}/no-asistida`),
  getHistorial:     (id)                 => API.get(`/citas/${id}/historial`),
};
```

### 5.4 Colores de estado (TailwindCSS)

```javascript
// src/componentes/citas/InsigniaEstado.jsx
const ESTADO_STYLES = {
  PENDIENTE:    'bg-yellow-100 text-yellow-800 border-yellow-300',
  CONFIRMADA:   'bg-green-100  text-green-800  border-green-300',
  REPROGRAMADA: 'bg-blue-100   text-blue-800   border-blue-300',
  CANCELADA:    'bg-red-100    text-red-800    border-red-300',
  COMPLETADA:   'bg-gray-100   text-gray-700   border-gray-300',
  NO_ASISTIDA:  'bg-orange-100 text-orange-800 border-orange-300',
};
```

---

## 6. Lógica de Negocio y Reglas

### 6.1 Reglas de Agendamiento

- Un slot dura exactamente `duracion_slot` minutos definidos en `disponibilidad`.
- No se permiten citas solapadas para el mismo psicólogo (estado `PENDIENTE` o `CONFIRMADA`).
- No se pueden agendar citas en el pasado.
- Un paciente no puede tener dos citas `PENDIENTE` o `CONFIRMADA` con el mismo psicólogo en el mismo día.

### 6.2 Reglas de Cancelación

- El **Paciente** solo puede cancelar con al menos **24 horas de anticipación**. Fuera de ese plazo, queda registrado como cancelación tardía.
- El **Psicólogo** puede cancelar hasta 2 horas antes.
- El **Admin** puede cancelar en cualquier momento.
- Una cita `COMPLETADA` o ya `CANCELADA` no puede cancelarse.

### 6.3 Reglas de Reprogramación

- Solo citas en estado `PENDIENTE` o `CONFIRMADA` pueden reprogramarse.
- Al reprogramar, el estado pasa a `REPROGRAMADA` y requiere nueva confirmación del psicólogo.
- Se guarda la referencia a la cita original en `reprogramada_desde`.

### 6.4 Generación de Slots

```
Para una fecha dada:
1. Determinar el día_semana (0=Lunes ... 6=Domingo)
2. Buscar bloques en `disponibilidad` para ese psicologo_id y dia_semana
3. Para cada bloque: generar slots desde hora_inicio hasta hora_fin con paso=duracion_slot
4. Verificar que la fecha no esté en `excepciones_disponibilidad`
5. Para cada slot generado, verificar que no se solape con una cita existente
6. Retornar lista de slots libres con formato { hora_inicio, hora_fin, disponible: true }
```

---

## 7. Seguridad y Autorización

### 7.1 Decoradores de Flask

```python
# app/utils/auth.py

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def requiere_rol(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('rol') not in roles:
                return {'error': 'Acceso no autorizado'}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Uso:
@bp.route('/citas', methods=['POST'])
@requiere_rol('paciente')
def agendar_cita():
    ...
```

### 7.2 Validación de Pertenencia

Antes de cualquier acción sobre una cita, verificar que:
- El `paciente_id` o `psicologo_id` de la cita coincide con el `user_id` del JWT.
- Los administradores omiten esta verificación.

### 7.3 Validación de Inputs con Marshmallow

Definir schemas estrictos para todos los endpoints. Ejemplo:

```python
# app/schemas/cita_schema.py
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime

class AgendarCitaSchema(Schema):
    psicologo_id    = fields.UUID(required=True)
    fecha_hora_inicio = fields.DateTime(required=True)
    modalidad       = fields.Str(validate=validate.OneOf(['VIRTUAL', 'PRESENCIAL']), load_default='VIRTUAL')
    motivo_consulta = fields.Str(validate=validate.Length(max=500))

    @validates('fecha_hora_inicio')
    def no_en_el_pasado(self, value):
        if value < datetime.utcnow():
            raise ValidationError('No se pueden agendar citas en el pasado.')
```

---

## 8. Integración con Otros Servicios

### 8.1 Servicio de Usuarios (puerto 5001)

El `servicio-citas` necesita datos del usuario (nombre, email, rol) para respuestas enriquecidas. Opciones:

- **Opción A (recomendada):** El frontend combina las respuestas — llama al gateway por separado y une los datos en el cliente.
- **Opción B:** El `servicio-citas` hace una llamada HTTP interna al `servicio-usuarios` para enriquecer respuestas. Usar variables de entorno para la URL interna.

```python
# Solo si se elige Opción B
import requests, os

def obtener_info_usuario(user_id, token):
    url = f"{os.getenv('SERVICIO_USUARIOS_URL')}/usuarios/{user_id}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=3)
    return resp.json() if resp.ok else {}
```

### 8.2 Servicio de Teleconsulta (puerto 5003) — Futuro

Al confirmar una cita con `modalidad=VIRTUAL`, el `servicio-citas` podrá notificar al `servicio-teleconsulta` para crear automáticamente una reunión de Zoom y adjuntar el enlace a la cita.

```python
# Stub para llamada futura al servicio-teleconsulta
def crear_reunion_zoom(cita_id, psicologo_id, paciente_id, fecha_hora):
    # POST http://servicio-teleconsulta:5003/reuniones
    pass
```

### 8.3 Notificaciones — Futuro

Integrar con DynamoDB (tablas de notificaciones) para enviar recordatorios automáticos 24h y 1h antes de la cita.

---

## 9. Orden de Implementación (Sprints)

### Sprint 1 — Fundamentos del Backend (Semana 1–2)

1. Crear `ejecutar.py` y la factory de Flask en `app/__init__.py` con Flask-Migrate integrado.
2. Definir modelos SQLAlchemy en `app/modelos/` con el esquema `citas_schema`.
3. Inicializar y ejecutar las migraciones siguiendo el mismo patrón que `servicio-usuarios`:
   ```powershell
   flask --app ejecutar.py db init
   flask --app ejecutar.py db migrate -m "esquema inicial de citas"
   flask --app ejecutar.py db upgrade
   ```
4. Crear `datos_iniciales.py` con citas y disponibilidad de demo vinculadas a los usuarios seed existentes.
5. Implementar la lógica de disponibilidad en `servicios/servicio_disponibilidad.py`:
   - CRUD de bloques horarios.
   - CRUD de excepciones.
   - Generación de slots.
6. Implementar endpoints de disponibilidad y probar con Postman/Insomnia.
7. Agregar `servicio-citas` al `docker-compose.yml` y verificar con:
   ```powershell
   docker compose up servicio-citas
   ```

### Sprint 2 — Lógica Central de Citas (Semana 2–3)

6. Implementar `cita_service.py` completo:
   - `agendar_cita` con todas las validaciones.
   - `confirmar_cita` / `cancelar_cita` / `reprogramar_cita`.
   - `completar_cita` / `marcar_no_asistida`.
   - Registro automático en `historial_cambios_citas`.
7. Implementar todos los endpoints REST en `citas_routes.py`.
8. Agregar reglas de proxy en el API Gateway.
9. Pruebas de integración backend completas.

### Sprint 3 — Frontend Base (Semana 3–4)

10. Crear `citasApi.js` y los hooks `useCitas.js` y `useDisponibilidad.js`.
11. Implementar `EstadoBadge.jsx` y `TarjetaCita.jsx`.
12. Implementar `ListaCitas.jsx` con filtros básicos (para los 3 roles).
13. Implementar `SlotSelector.jsx` (lista de horarios disponibles).
14. Implementar flujo de agendamiento: `AgendarCitaPage.jsx` + `ModalAgendarCita.jsx`.
15. Conectar rutas en el router de React y proteger por rol.

### Sprint 4 — Frontend Avanzado y Calendario (Semana 4–5)

16. Implementar `CalendarioSemanal.jsx` con navegación y marcadores de citas.
17. Implementar `CalendarioMensual.jsx` con puntos indicadores de ocupación.
18. Implementar `DetalleCitaPage.jsx` con botones de acción contextuales por rol.
19. Implementar `ModalReprogramar.jsx` y `ModalCancelar.jsx`.
20. Implementar `GestorDisponibilidad.jsx` para el panel del psicólogo.
21. Implementar `HistorialCita.jsx` con timeline visual (Framer Motion).

### Sprint 5 — Pulido y QA (Semana 5–6)

22. Pruebas end-to-end de todos los flujos por rol.
23. Validar políticas de cancelación con anticipación.
24. Manejo de errores en el frontend (estados de carga, errores de red, validaciones).
25. Revisión de accesibilidad y responsividad mobile.
26. Preparar variables de entorno para producción en AWS Secrets Manager.

---

## 10. Estructura de Archivos Propuesta

```
monorepo/
├── services/
│   ├── gateway/              # Puerto 5000 (ya existente — agregar rutas)
│   ├── users-service/        # Puerto 5001 (ya existente)
│   └── citas-service/        # Puerto 5002 ← NUEVO
│       ├── app/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── models/
│       │   │   ├── cita.py
│       │   │   ├── disponibilidad.py
│       │   │   └── historial.py
│       │   ├── schemas/
│       │   │   ├── cita_schema.py
│       │   │   └── disponibilidad_schema.py
│       │   ├── services/
│       │   │   ├── cita_service.py
│       │   │   └── disponibilidad_service.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── citas_routes.py
│       │   │   └── disponibilidad_routes.py
│       │   └── utils/
│       │       ├── auth.py
│       │       └── helpers.py
│       ├── migrations/
│       │   └── 001_initial_schema.sql
│       ├── tests/
│       │   ├── test_disponibilidad.py
│       │   └── test_citas.py
│       ├── Dockerfile
│       ├── requirements.txt
│       └── run.py
└── frontend/
    └── src/
        ├── pages/citas/
        ├── components/citas/
        ├── hooks/
        └── services/citasApi.js
```

---

## 11. Docker y Variables de Entorno

### Agregar al `docker-compose.yml`

```yaml
citas-service:
  build: ./services/citas-service
  container_name: citas_service
  ports:
    - "5002:5002"
  environment:
    - FLASK_ENV=development
    - DATABASE_URL=postgresql://postgres:password@postgres:5432/psicoconecta
    - DB_SCHEMA=citas_schema
    - JWT_SECRET_KEY=${JWT_SECRET_KEY}         # Misma clave que users-service
    - USERS_SERVICE_URL=http://users-service:5001
  depends_on:
    - postgres
  networks:
    - psicoconecta-network
```

### Variables de Entorno requeridas (`.env`)

```dotenv
# Compartidas
JWT_SECRET_KEY=super_secreto_compartido

# citas-service específicas
DATABASE_URL=postgresql://usuario:password@localhost:5432/psicoconecta
DB_SCHEMA=citas_schema
USERS_SERVICE_URL=http://localhost:5001
CANCEL_MIN_HOURS_PATIENT=24    # Horas mínimas para cancelar (paciente)
CANCEL_MIN_HOURS_PSYCH=2       # Horas mínimas para cancelar (psicólogo)
```

### Migración de base de datos

Al iniciar el contenedor, ejecutar:

```sql
-- migrations/001_initial_schema.sql
CREATE SCHEMA IF NOT EXISTS citas_schema;
-- Luego el resto de tablas del punto 2
```

---

## 12. Pruebas

### Backend — Casos de prueba prioritarios

```python
# tests/test_citas.py

# Agendamiento exitoso
def test_agendar_cita_exitoso()

# Slot ya ocupado
def test_agendar_cita_slot_no_disponible()

# Intento de agendar en el pasado
def test_agendar_cita_en_pasado()

# Cancelación dentro del plazo permitido
def test_cancelar_cita_dentro_plazo()

# Cancelación fuera del plazo (paciente)
def test_cancelar_cita_fuera_plazo_paciente()

# Reprogramación exitosa
def test_reprogramar_cita_exitoso()

# Confirmación por psicólogo correcto
def test_confirmar_cita_psicologo_correcto()

# Acceso denegado por rol incorrecto
def test_confirmar_cita_rol_invalido()

# Generación de slots libres
def test_get_slots_dia_sin_excepciones()
def test_get_slots_dia_con_excepcion()
```

### Frontend — Flujos a probar manualmente

- [ ] Paciente agenda cita → aparece en estado PENDIENTE para ambos
- [ ] Psicólogo confirma → estado cambia a CONFIRMADA
- [ ] Paciente reprograma → estado cambia a REPROGRAMADA, requiere nueva confirmación
- [ ] Admin cancela cualquier cita con motivo
- [ ] Psicólogo configura disponibilidad y los slots aparecen correctamente
- [ ] Psicólogo bloquea un día y no aparecen slots para ese día
- [ ] El historial de cambios refleja cada acción con timestamp y actor

---

*Fin del plan de implementación. Cada sprint puede ajustarse según la velocidad del equipo. Se recomienda comenzar siempre por el Sprint 1 (migraciones y backend de disponibilidad) ya que es la base de toda la lógica de agendamiento.*
