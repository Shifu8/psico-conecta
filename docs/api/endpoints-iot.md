# Endpoints del Servicio de IoT e Inteligencia

Descripción corta:
Este documento describe las rutas proyectadas para el servicio de inteligencia artificial y el Internet de las Cosas, responsable del análisis de emociones y la gestión de lecturas biométricas.

## 1. Referencia de API

Base URL local: `http://localhost:5005` (o a través del API Gateway en `http://localhost:5000/iot`)

*(Nota: Los siguientes endpoints corresponden a la estructura base y están marcados como pendientes de validar hasta completar su integración final con DynamoDB y AWS IoT)*

*   **POST `/api/iot/lectura`** (Pendiente de validar)
    *   **Propósito:** Recibe flujos de datos biométricos desde dispositivos externos.
*   **POST `/api/iot/analisis-emocion`** (Pendiente de validar)
    *   **Propósito:** Procesa clips de audio o imágenes para predecir el estado emocional del paciente usando modelos de machine learning.
*   **GET `/api/iot/reporte/:paciente_id`** (Pendiente de validar)
    *   **Propósito:** Retorna un agregado estadístico de las emociones registradas durante sesiones previas.
