# Corrección para el despliegue AWS existente

Este paquete actualiza el clúster ECS `psicoconecta`, el bucket S3 y la distribución CloudFront ya existentes. No crea una segunda aplicación.

## Secretos obligatorios

Configurar en GitHub Actions o conservar previamente en AWS Secrets Manager:

- `DATABASE_URL`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `TELECONSULTA_INTERNAL_TOKEN`
- `PAGOS_INTERNAL_TOKEN`
- `ZOOM_ACCOUNT_ID`
- `ZOOM_CLIENT_ID`
- `ZOOM_CLIENT_SECRET`
- `ZOOM_HOST_USER_ID`
- `ZOOM_WEBHOOK_SECRET_TOKEN`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

Los nombres creados en Secrets Manager usan el prefijo `psicoconecta/`.

## Webhooks públicos

- Zoom: `https://d1wkhs3cq8vcom.cloudfront.net/api/teleconsultas/webhooks/zoom`
- Stripe: `https://d1wkhs3cq8vcom.cloudfront.net/api/pagos/webhooks/stripe`

En Zoom y Stripe se deben registrar exactamente esas URL. El secreto del webhook de cada proveedor debe coincidir con el almacenado en AWS.

## Base de datos

Todos los servicios usan el mismo PostgreSQL indicado por `DATABASE_URL`, separados por esquemas. Si existe el esquema antiguo de pagos, las tablas se conservan con sufijo `_legacy` y se crean las nuevas tablas compatibles con Stripe.
