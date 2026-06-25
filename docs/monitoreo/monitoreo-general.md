# Monitoreo general

Descripción corta:
Este documento proporciona una visión global sobre la estrategia de observabilidad y seguimiento implementada en PsicoConecta, tanto a nivel de infraestructura como a nivel de producto.

## 1. Estrategia de observabilidad

El monitoreo de la plataforma se divide en tres pilares principales:
1. **Infraestructura y Rendimiento:** Monitoreo de uso de CPU, memoria, estado de contenedores y bases de datos.
2. **Logs y Errores:** Recolección centralizada de trazas de error para facilitar la depuración.
3. **Analítica de Producto:** Seguimiento del comportamiento de los usuarios (inicios de sesión, retención, uso de funciones).

## 2. Herramientas implementadas

*   **Auditoría Interna (PostgreSQL):** Se ha implementado una tabla `eventos_auditoria` que registra acciones administrativas, inicios de sesión y registros de forma inmutable. Esto es visible directamente desde el panel de administración del frontend.
*   **PostHog:** Integrado en el frontend de React para analítica de eventos (funnels, retención y grabaciones de sesión). Puede funcionar en modalidad Cloud o auto-hospedado (Self-Hosted).
*   **AWS CloudWatch:** Plataforma base en la nube para gestionar métricas de contenedores ECS, recolectar registros (logs) del backend y definir alarmas operacionales.
