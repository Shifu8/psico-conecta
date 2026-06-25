# Configuración de la base de datos

Descripción corta:
Este documento proporciona las instrucciones y parámetros para establecer la conexión a las bases de datos de la plataforma, detallando la inicialización en entornos locales.

## 1. Conexión local con Docker

El proyecto utiliza una instancia de `postgres:16-alpine` orquestada mediante Docker Compose.

*   **Host:** `localhost` (o `postgres` en la red interna de Docker)
*   **Puerto:** `5432`
*   **Usuario por defecto:** `postgres`
*   **Contraseña por defecto:** `postgres`
*   **Nombre de la base de datos:** `psicoconecta`

## 2. Inicialización automática

Cuando el contenedor de PostgreSQL se levanta por primera vez, ejecuta automáticamente todos los scripts `.sql` ubicados en `infraestructura/postgres/`. En el entorno actual, existe el archivo `01-inicializar-esquemas.sql` que se encarga de crear los esquemas aislados (`usuarios_schema`, `citas_schema`, etc.) para garantizar la separación de datos de los microservicios.

## 3. Carga de datos semilla (Seed)

Para facilitar el desarrollo, el contenedor `servicio-usuarios` ejecuta automáticamente el script de Python `datos_iniciales.py` en su proceso de arranque. Este script:
1. Conecta a la base de datos.
2. Crea las tablas de usuarios y roles si no existen, mediante SQLAlchemy.
3. Inserta usuarios de prueba (Administrador, Psicólogo y Paciente) con contraseñas encriptadas.

## 4. Conexión en producción

En entornos productivos como AWS, la cadena de conexión se construye dinámicamente inyectando las credenciales almacenadas en AWS Secrets Manager hacia la variable de entorno `DATABASE_URL`.
