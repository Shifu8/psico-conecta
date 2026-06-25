# Pruebas de integración

Descripción corta:
Este documento describe el enfoque para verificar que los diferentes microservicios, bases de datos y sistemas externos de PsicoConecta interactúen correctamente entre sí.

## 1. Alcance de las pruebas

Las pruebas de integración se centran en los límites del sistema:
*   Comunicación entre Frontend y API Gateway.
*   Comunicación entre API Gateway y Microservicios.
*   Conectividad y operaciones CRUD desde Microservicios hacia PostgreSQL.
*   Integración con APIs de terceros (Google, Zoom, Stripe).

## 2. Escenarios clave

### 2.1 Integración interna
*   **Validación de Tokens:** Verificar que un JWT emitido por el `servicio-usuarios` sea aceptado y decodificado correctamente por el `servicio-citas` al realizar una petición protegida.
*   **Persistencia:** Asegurar que los datos guardados en un esquema de PostgreSQL mediante SQLAlchemy sean recuperables de forma consistente.

### 2.2 Integración externa
*   **Google OAuth:** Probar el flujo completo donde el frontend envía un Token ID a la API, la API consulta a los servidores de Google para verificarlo, y la base de datos registra la cuenta en PostgreSQL.
*   **Gmail API:** Verificar que el `servicio-usuarios` pueda despachar correos electrónicos reales invocando el servicio de Google Cloud.
