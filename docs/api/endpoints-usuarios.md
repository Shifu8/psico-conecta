# Endpoints del Servicio de Usuarios

Descripción corta:
Este documento enumera los endpoints expuestos por el microservicio de usuarios, abarcando registro, inicio de sesión, recuperación de contraseña y administración de cuentas.

## 1. Referencia de API

Base URL local: `http://localhost:5001` (o a través del API Gateway en `http://localhost:5000/usuarios`)

### 1.1 Autenticación

*   **POST `/api/auth/register`**
    *   **Propósito:** Registra un nuevo usuario en el sistema.
    *   **Cuerpo (JSON):** `nombre`, `email`, `password`.
*   **POST `/api/auth/login`**
    *   **Propósito:** Inicia sesión con credenciales tradicionales.
    *   **Respuesta:** Token JWT y datos básicos del usuario.
*   **POST `/api/auth/google-login`**
    *   **Propósito:** Inicia sesión validando un Token ID proporcionado por Google OAuth.
    *   **Cuerpo (JSON):** `token` (ID token de Google).

### 1.2 Recuperación de contraseña

*   **POST `/api/auth/recuperar-password`**
    *   **Propósito:** Solicita un enlace temporal enviado al correo del usuario.
    *   **Cuerpo (JSON):** `email`.
*   **POST `/api/auth/reset-password`**
    *   **Propósito:** Define una nueva contraseña usando el token temporal recibido por correo.
    *   **Cuerpo (JSON):** `token`, `nueva_password`.

### 1.3 Administración y Perfil

*   **GET `/api/usuarios/perfil`** (Pendiente de validar)
    *   **Propósito:** Obtiene la información del usuario autenticado.
    *   **Cabeceras:** `Authorization: Bearer <token>`
*   **GET `/api/admin/usuarios`** (Pendiente de validar)
    *   **Propósito:** Lista todos los usuarios (solo para rol Administrador).
