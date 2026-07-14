# Servicio de teleconsultas

## Objetivo

Gestionar reuniones privadas de Zoom vinculadas a las citas virtuales de PsicoConecta.
Una reunión solo se prepara cuando la cita está en modalidad `VIRTUAL` y estado
`CONFIRMADA`.

## Flujo

1. El paciente agenda una cita virtual.
2. El psicólogo confirma la cita.
3. `servicio-citas` notifica internamente a `servicio-teleconsulta`.
4. El servicio crea la reunión mediante Zoom Server-to-Server OAuth y guarda solamente
   el enlace de participante.
5. El paciente puede obtener su enlace desde 10 minutos antes.
6. El psicólogo obtiene un enlace de anfitrión nuevo desde 15 minutos antes.
7. Si la cita se reprograma o cancela, la reunión anterior se elimina de Zoom.
8. Los webhooks actualizan la sesión cuando la reunión inicia o finaliza.

## Endpoints públicos

- `GET /api/teleconsultas/mis-sesiones`
- `GET /api/teleconsultas/cita/<uuid:cita_id>`
- `POST /api/teleconsultas/cita/<uuid:cita_id>/acceso`
- `POST /api/teleconsultas/webhooks/zoom`

## Endpoint interno

- `POST /api/teleconsultas/interna/citas/sincronizar`

Requiere la cabecera `X-Internal-Token` compartida con `servicio-citas`.

## Variables principales

- `DATABASE_URL`
- `DB_SCHEMA=teleconsulta_schema`
- `JWT_SECRET_KEY`
- `USERS_SERVICE_URL`
- `CITAS_SERVICE_URL`
- `TELECONSULTA_INTERNAL_TOKEN`
- `ZOOM_ACCOUNT_ID`
- `ZOOM_CLIENT_ID`
- `ZOOM_CLIENT_SECRET`
- `ZOOM_HOST_USER_ID`
- `ZOOM_HOSTS_JSON`
- `ZOOM_WEBHOOK_SECRET_TOKEN`

`ZOOM_HOSTS_JSON` permite asignar una cuenta Zoom por psicólogo. Ejemplo:

```json
{"2":"psicologo1@dominio.com","3":"psicologo2@dominio.com"}
```

Si no se define un valor para un psicólogo, se utiliza `ZOOM_HOST_USER_ID`.

## Seguridad

- JWT compartido con el servicio de usuarios.
- Comprobación remota de usuario activo cuando `VALIDAR_USUARIO_REMOTO=true`.
- Sala de espera habilitada.
- Ingreso antes del anfitrión deshabilitado.
- Sin grabación automática.
- El enlace `start_url` del anfitrión no se almacena y se solicita a Zoom al ingresar.
- El tema de la reunión no expone nombres ni motivos clínicos.
- Webhooks validados mediante HMAC SHA-256.

## Base de datos

Esquema `teleconsulta_schema`:

- `sesiones_zoom`
- `historial_sesiones`

La migración se encuentra en:

```text
infraestructura/postgres/migracion_modulo_teleconsultas.sql
```

## Pruebas

```powershell
docker compose exec servicio-teleconsulta pytest -q -p no:cacheprovider
```

Resultado esperado:

```text
......                                                                   [100%]
6 passed
```
