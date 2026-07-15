# Despliegue de pagos y teleconsultas en el entorno AWS existente

Este procedimiento actualiza el entorno que ya usa PsicoConecta. No crea otro
clúster, otra distribución CloudFront ni otro bucket del frontend.

## Recursos reutilizados

- Región: `us-east-2`.
- Clúster ECS: `psicoconecta`.
- Servicio público: `puerta-enlace`.
- Bucket: `psicoconecta-frontend-060899556466`.
- Frontend y API pública: `https://d1wkhs3cq8vcom.cloudfront.net`.

El workflow puede crear únicamente los servicios internos que falten dentro del
mismo clúster y los repositorios ECR necesarios. La red y el balanceador se toman
del despliegue existente.

## Secretos obligatorios

Configura estos nombres en **GitHub > Settings > Secrets and variables > Actions**
o directamente en AWS Secrets Manager con el prefijo `psicoconecta/`:

| Secreto | Uso |
|---|---|
| `DATABASE_URL` | Conexión PostgreSQL/RDS compartida por los servicios. |
| `SECRET_KEY` | Firma interna de Flask. |
| `JWT_SECRET_KEY` | Debe ser idéntica en usuarios, citas, pagos y teleconsulta. |
| `TELECONSULTA_INTERNAL_TOKEN` | Comunicación citas → teleconsulta. |
| `PAGOS_INTERNAL_TOKEN` | Comunicación citas/teleconsulta → pagos. |
| `ZOOM_ACCOUNT_ID` | Cuenta de la aplicación Server-to-Server OAuth de Zoom. |
| `ZOOM_CLIENT_ID` | Cliente de Zoom. |
| `ZOOM_CLIENT_SECRET` | Secreto de Zoom. |
| `ZOOM_HOST_USER_ID` | Usuario anfitrión autorizado para crear reuniones. |
| `ZOOM_WEBHOOK_SECRET_TOKEN` | Validación de eventos enviados por Zoom. |
| `STRIPE_SECRET_KEY` | Clave privada de Stripe; usa `sk_test_...` para pruebas. |
| `STRIPE_WEBHOOK_SECRET` | Firma del endpoint de eventos de Stripe. |

El workflow actualiza Secrets Manager cuando el valor existe en GitHub. Si el
valor no está en GitHub pero ya existe en AWS, conserva el valor desplegado.
Nunca se escriben claves privadas en el repositorio ni en el frontend.

## URLs públicas para proveedores externos

Configura los webhooks con estas direcciones:

- Zoom: `https://d1wkhs3cq8vcom.cloudfront.net/api/teleconsultas/webhooks/zoom`
- Stripe: `https://d1wkhs3cq8vcom.cloudfront.net/api/pagos/webhooks/stripe`

En Zoom debe activarse al menos la recepción de eventos de inicio, finalización
y eliminación de reuniones. En Stripe deben habilitarse los eventos de Checkout,
PaymentIntent, reembolsos y disputas utilizados por el servicio.

## Base de datos

`DATABASE_URL` debe apuntar a PostgreSQL accesible desde las tareas ECS, por
ejemplo:

```text
postgresql://USUARIO:CONTRASENA@ENDPOINT-RDS:5432/psicoconecta
```

Durante el arranque cada servicio crea su esquema si falta. El servicio de pagos
detecta las tablas antiguas incompatibles, las renombra con el sufijo
`legacy_FECHA` y crea las tablas actuales sin eliminar el respaldo.

## Despliegue

El workflow `.github/workflows/deploy.yml` se ejecuta con cada push a `main` o
manualmente desde GitHub Actions. El proceso:

1. Comprueba el clúster existente.
2. Conserva o actualiza los secretos de AWS.
3. Construye y prueba las imágenes.
4. Actualiza las tareas del mismo clúster ECS.
5. Configura comunicación privada mediante ECS Service Connect.
6. Dirige `/api/*` del balanceador existente hacia la puerta de enlace.
7. Compila el frontend con la URL CloudFront para todos los módulos.
8. Sincroniza `dist` con el bucket existente e invalida CloudFront.

## Verificación

Después del despliegue revisa:

```text
https://d1wkhs3cq8vcom.cloudfront.net/health
https://d1wkhs3cq8vcom.cloudfront.net/api/usuarios/autenticacion/google/configuracion
```

Para pagos, confirma una cita virtual, inicia Checkout con un paciente y verifica
el evento en el panel de Stripe. Para teleconsulta, abre la cita confirmada y
solicita acceso; la reunión debe crearse desde el backend y el enlace debe poder
abrirse desde cualquier equipo con conexión a Internet.
