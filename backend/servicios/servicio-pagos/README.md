# Servicio de pagos de PsicoConecta

Servicio Flask para cobrar consultas mediante Stripe Checkout sin recibir ni almacenar datos de tarjeta.

## Funciones

- Crea un pago al confirmar una cita.
- Calcula la tarifa en el servidor.
- Genera sesiones alojadas de Stripe Checkout.
- Sincroniza pagos por retorno del navegador y por webhooks firmados.
- Guarda comprobantes, transacciones e historial.
- Permite reembolsos totales y parciales al administrador.
- Reembolsa automáticamente al cancelar una cita cuando está habilitado.
- Transfiere el pago a la nueva cita cuando existe una reprogramación.
- Puede impedir el acceso a Zoom hasta confirmar el pago.

## Endpoints principales

- `GET /health`
- `GET /api/pagos/mis-pagos`
- `GET /api/pagos` — administrador
- `GET /api/pagos/<pago_id>`
- `GET /api/pagos/cita/<cita_id>`
- `POST /api/pagos/cita/<cita_id>/checkout`
- `POST /api/pagos/checkout/<session_id>/sincronizar`
- `POST /api/pagos/<pago_id>/reembolsar` — administrador
- `GET|POST /api/pagos/tarifas` — administrador
- `DELETE /api/pagos/tarifas/<tarifa_id>` — administrador
- `POST /api/pagos/webhooks/stripe`

## Seguridad

- Los montos se calculan en el backend; el navegador nunca decide el precio.
- Los endpoints de usuario exigen JWT y rol.
- Las comunicaciones desde citas y teleconsultas usan `X-Internal-Token`.
- Los webhooks se validan con `STRIPE_WEBHOOK_SECRET`.
- La clave secreta de Stripe solo debe existir en `.env`, nunca en GitHub.

## Pruebas

```powershell
docker compose exec servicio-pagos pytest -q -p no:cacheprovider
```
