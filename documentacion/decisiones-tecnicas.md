# Decisiones técnicas definitivas

- Backend: Python Flask para todos los microservicios.
- Frontend: React, Vite, TailwindCSS, Framer Motion, Axios y React Router.
- Autenticación: Amazon Cognito y JWT local para desarrollo.
- Google: proveedor federado de Cognito, sin OAuth directo en Flask.
- Recuperación: Gmail API, sin SMTP.
- Persistencia relacional: una instancia PostgreSQL con esquemas separados.
- Teleconsulta: Zoom API.
- Pagos: Stripe Sandbox, sin cobros reales.
- IoT: DynamoDB, AWS IoT Core, MQTT y WebSockets.
- Archivos: Amazon S3.
- Cloud: AWS.

No se mantienen alternativas tecnológicas abiertas.

