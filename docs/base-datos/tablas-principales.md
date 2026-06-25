# Tablas principales

Descripción corta:
Este documento enlista y describe las entidades más importantes del modelo relacional implementado en PostgreSQL para el funcionamiento del módulo de Usuarios.

## 1. Esquema `usuarios_schema`

Este esquema centraliza toda la información relacionada con la identidad y permisos de los actores del sistema.

### 1.1 Tabla `usuarios`
Es la tabla núcleo del sistema.
*   **Columnas clave:**
    *   `id`: UUID (Clave Primaria).
    *   `email`: String (Único, índice para inicio de sesión).
    *   `password_hash`: String (Contraseña encriptada, nula si usa OAuth).
    *   `google_id`: String (Opcional, almacena el ID provisto por Google).
    *   `rol_id`: Integer (Clave Foránea, relación con la tabla roles).
    *   `activo`: Boolean (Determina si el usuario puede iniciar sesión).

### 1.2 Tabla `roles`
Define los niveles de acceso del sistema.
*   **Columnas clave:**
    *   `id`: Integer (Clave Primaria).
    *   `nombre`: String (Único).

*(Nota: Las tablas para citas, teleconsulta y pagos se detallarán en este documento conforme los microservicios respectivos completen su fase de desarrollo estructural y definan sus modelos definitivos mediante SQLAlchemy).*
