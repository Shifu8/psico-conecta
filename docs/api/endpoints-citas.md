# Endpoints del Servicio de Citas

Descripción corta:
Este documento describe las rutas API proyectadas para el servicio de citas, que manejará la disponibilidad de psicólogos y la programación de terapias.

## 1. Referencia de API

Base URL local: `http://localhost:5002` (o a través del API Gateway en `http://localhost:5000/citas`)

*(Nota: Los siguientes endpoints corresponden a la estructura base y están marcados como pendientes de validar hasta que la lógica de negocio esté completamente expuesta)*

*   **GET `/api/citas/disponibilidad`** (Pendiente de validar)
    *   **Propósito:** Consulta los horarios libres de un psicólogo específico.
*   **POST `/api/citas/agendar`** (Pendiente de validar)
    *   **Propósito:** Crea una nueva reserva de cita para un paciente.
*   **PUT `/api/citas/reagendar/:id`** (Pendiente de validar)
    *   **Propósito:** Modifica la fecha u hora de una cita existente.
*   **DELETE `/api/citas/cancelar/:id`** (Pendiente de validar)
    *   **Propósito:** Cancela una cita y libera el horario.
