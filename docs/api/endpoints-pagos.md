# Endpoints del Servicio de Pagos

Descripción corta:
Este documento describe las rutas proyectadas para el servicio de pagos, el cual manejará las transacciones financieras a través de Stripe Sandbox.

## 1. Referencia de API

Base URL local: `http://localhost:5004` (o a través del API Gateway en `http://localhost:5000/pagos`)

*(Nota: Los siguientes endpoints corresponden a la estructura base y están marcados como pendientes de validar hasta completar su integración final)*

*   **POST `/api/pagos/crear-intencion`** (Pendiente de validar)
    *   **Propósito:** Genera un "Payment Intent" en Stripe para cobrar una cita.
*   **POST `/api/pagos/webhook`** (Pendiente de validar)
    *   **Propósito:** Endpoint público y seguro para recibir confirmaciones de pago asíncronas desde los servidores de Stripe.
*   **GET `/api/pagos/historial`** (Pendiente de validar)
    *   **Propósito:** Retorna la lista de transacciones previas de un paciente.
