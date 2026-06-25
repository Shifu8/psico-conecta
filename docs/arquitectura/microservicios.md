# Microservicios

Descripción corta:
Este documento detalla la estructura y el propósito de cada uno de los microservicios que componen la plataforma PsicoConecta, explicando sus responsabilidades principales dentro del sistema.

## 1. Descripción de microservicios

El sistema se compone de varios microservicios independientes, que corren sobre puertos distintos y operan de forma aislada, manteniendo el principio de responsabilidad única.

### 1.1 Puerta de enlace (API Gateway)
- **Directorio:** `backend/puerta-enlace-api`
- **Puerto local:** `5000`
- **Propósito:** Actúa como el único punto de entrada para el frontend. Redirige el tráfico hacia el microservicio correspondiente, maneja políticas básicas de CORS y balanceo.

### 1.2 Servicio de Usuarios
- **Directorio:** `backend/servicios/servicio-usuarios`
- **Puerto local:** `5001`
- **Propósito:** Encargado de la gestión de identidades, autenticación (local y Google OAuth), emisión y validación de tokens JWT, recuperación de contraseñas mediante Gmail API y gestión de perfiles.

### 1.3 Servicio de Citas
- **Directorio:** `backend/servicios/servicio-citas`
- **Puerto local:** `5002`
- **Propósito:** Responsable de programar, reagendar y cancelar terapias. Mantiene la disponibilidad de los psicólogos y valida que no existan conflictos de horarios.

### 1.4 Servicio de Teleconsulta
- **Directorio:** `backend/servicios/servicio-teleconsulta`
- **Puerto local:** `5003`
- **Propósito:** Gestiona la integración con proveedores de videollamada como Zoom API, generando enlaces de reuniones seguros y controlando la duración y estado de las consultas online.

### 1.5 Servicio de Pagos
- **Directorio:** `backend/servicios/servicio-pagos`
- **Puerto local:** `5004`
- **Propósito:** Procesa las transacciones de pago mediante integraciones externas (Stripe Sandbox). Valida montos, procesa devoluciones y emite recibos.

### 1.6 Servicio de Inteligencia e IoT
- **Directorio:** `backend/servicios/servicio-inteligencia-iot`
- **Puerto local:** `5005`
- **Propósito:** Procesa y almacena lecturas biométricas y análisis de emociones enviadas desde dispositivos, utilizando AWS IoT Core y DynamoDB para manejar alto volumen de datos no relacionales.
