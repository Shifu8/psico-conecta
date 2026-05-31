# Despliegue futuro en AWS

| Componente | Servicio AWS |
| --- | --- |
| Frontend | S3 + CloudFront o Amplify |
| Microservicios Flask | ECS Fargate |
| Base relacional | RDS PostgreSQL |
| Autenticación y Google | Cognito |
| Archivos | S3 |
| Telemetría IoT | AWS IoT Core + DynamoDB |
| Secretos | Secrets Manager |
| Tareas asíncronas futuras | Lambda |

La entrega local no incluye credenciales ni recursos cloud reales. Producción
requiere HTTPS, observabilidad, backups, IAM de mínimo privilegio y CI/CD.

