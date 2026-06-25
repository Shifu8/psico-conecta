# Endpoints del Servicio de Teleconsulta

Descripción corta:
Este documento describe las rutas proyectadas para el servicio de teleconsulta, encargado de integrar videollamadas mediante la API de Zoom.

## 1. Referencia de API

Base URL local: `http://localhost:5003` (o a través del API Gateway en `http://localhost:5000/teleconsulta`)

*(Nota: Los siguientes endpoints corresponden a la estructura base y están marcados como pendientes de validar hasta completar su integración final)*

*   **POST `/api/teleconsulta/generar-enlace`** (Pendiente de validar)
    *   **Propósito:** Se comunica con Zoom API para generar una reunión única para una cita confirmada.
*   **GET `/api/teleconsulta/estado/:id`** (Pendiente de validar)
    *   **Propósito:** Consulta el estado de la sala (activa, finalizada, grabando).
