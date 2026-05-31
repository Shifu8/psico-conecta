# Arquitectura de microservicios

PsicoConecta separa responsabilidades por servicio Flask. La puerta de enlace
publica el catálogo de servicios y permite incorporar un proxy administrado en
AWS sin acoplar el código local.

| Servicio | Responsabilidad |
| --- | --- |
| Usuarios | Registro, JWT, perfiles, roles, permisos y recuperación Gmail API |
| Citas | Agenda, horarios disponibles e historial |
| Teleconsulta | Reuniones Zoom asociadas a citas e historial |
| Pagos | Operaciones Stripe Sandbox, transacciones y comprobantes |
| Inteligencia e IoT | Emociones, ESP32, MAX30102, MQTT y WebSockets |

Los servicios transaccionales comparten una instancia PostgreSQL con esquemas
separados. IoT usa DynamoDB y AWS IoT Core. Los archivos se almacenarán en S3.

