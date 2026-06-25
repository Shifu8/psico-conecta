# Comunicación entre servicios

Descripción corta:
Este documento explica los mecanismos mediante los cuales los distintos componentes de PsicoConecta (frontend, puerta de enlace y microservicios backend) interactúan entre sí.

## 1. Patrón de comunicación

La plataforma utiliza predominantemente un modelo de comunicación síncrona basado en REST sobre HTTP/HTTPS para las interacciones directas entre componentes.

### 1.1 Flujo desde el Frontend
1. El **Frontend** (React) no se comunica directamente con los microservicios backend.
2. Todas las peticiones del frontend se dirigen a la **Puerta de Enlace** (API Gateway).
3. La Puerta de Enlace analiza la ruta solicitada y reenvía la petición al microservicio interno correspondiente.

### 1.2 Flujo Interno (Microservicio a Microservicio)
Cuando un servicio necesita información de otro (por ejemplo, el Servicio de Citas necesita validar los datos de un usuario), se realiza una petición HTTP directa interna.
* En desarrollo local, se realiza apuntando al puerto expuesto localmente o al nombre del servicio en Docker (ej. `http://servicio-usuarios:5001`).
* Se utiliza un mecanismo de validación en el cual los tokens JWT se retransmiten a través de los encabezados HTTP (`Authorization: Bearer <token>`) para que el servicio receptor valide los permisos correspondientes.

## 2. Manejo de autenticación distribuida

1. El Servicio de Usuarios emite el JWT una vez validada la identidad (login convencional o Google OAuth).
2. El Frontend almacena el token y lo envía en el encabezado `Authorization` en cada petición posterior.
3. La Puerta de Enlace transfiere este encabezado.
4. Cada microservicio backend que recibe la petición valida el JWT (usando una clave compartida o solicitando validación al Servicio de Usuarios) antes de procesar la regla de negocio.

## 3. Consideraciones de escalabilidad futuras

Actualmente, la comunicación es altamente acoplada mediante REST. En futuras fases, procesos que no requieran respuesta inmediata (como el envío de correos, generación de reportes o procesamiento de datos IoT) podrán migrarse a esquemas de comunicación asíncrona mediante colas de mensajes (como Amazon SQS o RabbitMQ) para mejorar la resiliencia del sistema.
