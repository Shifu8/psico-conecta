# Pruebas funcionales

Descripción corta:
Este documento establece las directrices y casos de prueba principales para validar el correcto comportamiento de la plataforma desde la perspectiva del usuario.

## 1. Estrategia de pruebas funcionales

El objetivo es asegurar que las características principales de PsicoConecta cumplan con los requisitos de negocio, comportándose según lo esperado en escenarios normales y en casos de error predecibles.

## 2. Casos de prueba: Módulo de Usuarios

### 2.1 Registro e inicio de sesión
*   **Registro exitoso:** Validar que un nuevo correo y contraseña válida creen un usuario activo.
*   **Validación de correo duplicado:** El sistema debe denegar el registro si el correo ya existe.
*   **Inicio de sesión válido:** Un usuario registrado debe obtener un token JWT tras enviar credenciales válidas.
*   **Inicio con Google OAuth:** El botón de Google en el frontend debe generar una sesión válida en el backend comprobando que el correo coincida.

### 2.2 Recuperación de contraseña
*   **Solicitud de recuperación:** Un correo válido debe recibir el enlace de restablecimiento a través de Gmail API.
*   **Cambio exitoso:** El enlace debe permitir cambiar la contraseña solo si el token temporal no ha expirado.

## 3. Casos de prueba proyectados (Otros módulos)

*(Nota: Los siguientes casos aplicarán una vez completados los respectivos microservicios)*

*   **Citas:** Verificación de agendamiento sin colisiones de horario y cancelación exitosa liberando la franja.
*   **Teleconsulta:** Confirmación de que el enlace de Zoom generado corresponde al usuario y al bloque de la cita.
*   **Pagos:** Validación de pagos exitosos con tarjetas de prueba de Stripe Sandbox y manejo de tarjetas rechazadas.
