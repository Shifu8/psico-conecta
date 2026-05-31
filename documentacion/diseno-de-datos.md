# Diseño de datos

## PostgreSQL

Una sola instancia contiene separación lógica por esquema:

| Esquema | Tablas previstas |
| --- | --- |
| `usuarios_schema` | `usuarios`, `roles`, `permisos`, `roles_permisos`, `tokens_recuperacion`, `tokens_revocados` |
| `citas_schema` | `citas`, `horarios_disponibles`, `historial_citas` |
| `teleconsulta_schema` | `sesiones_zoom`, `historial_sesiones` |
| `pagos_schema` | `pagos`, `transacciones`, `comprobantes` |

## DynamoDB

El servicio IoT utiliza:

- `emociones`
- `lecturas_iot`
- `notificaciones`
- `logs_iot`

MongoDB no forma parte de la arquitectura.

