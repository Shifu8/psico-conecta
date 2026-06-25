# Pruebas de rendimiento

Descripción corta:
Este documento perfila las estrategias para validar que la plataforma soporte la carga esperada de usuarios concurrentes y mantenga tiempos de respuesta óptimos.

## 1. Estrategia de pruebas

Las pruebas de rendimiento se centran en identificar cuellos de botella en la base de datos y en los tiempos de respuesta de los microservicios, especialmente bajo situaciones de alta concurrencia.

## 2. Puntos críticos a evaluar

*   **API Gateway:** Capacidad para enrutar múltiples conexiones simultáneas sin aumentar significativamente la latencia.
*   **Base de Datos (PostgreSQL):** Rendimiento de consultas durante la lectura del perfil de usuario y la verificación de horarios disponibles de citas.
*   **Servicio de IoT:** Capacidad para ingerir ráfagas de datos en DynamoDB sin generar cuellos de botella en el microservicio.

*(Nota: La definición de herramientas específicas de carga como JMeter o Locust, así como los umbrales de aceptación, se detallarán en futuras fases del proyecto cuando el entorno de producción esté consolidado).*
