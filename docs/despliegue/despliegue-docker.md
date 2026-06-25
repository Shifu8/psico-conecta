# Despliegue con Docker

Descripción corta:
Este documento describe el uso de Docker y Docker Compose para desplegar los componentes de PsicoConecta, tanto para desarrollo local unificado como para escenarios de producción contenerizados.

## 1. Orquestación local (Docker Compose)

En la raíz del proyecto se encuentra el archivo `docker-compose.yml`. Este archivo define los servicios y redes necesarios para levantar la infraestructura base y los microservicios sin necesidad de instalar dependencias pesadas en la máquina anfitriona.

### 1.1 Servicios definidos

*   **postgres:** Instancia de PostgreSQL (versión 16 basada en Alpine) con montajes de volúmenes para persistencia y scripts de inicialización de esquemas (`infraestructura/postgres/inicializar_esquemas.sql`).
*   **pgadmin:** (Opcional, perfil `tools`) Interfaz gráfica para administración de la base de datos PostgreSQL.
*   **servicio-usuarios, servicio-citas, etc.:** Microservicios de backend configurados a partir de imágenes base ligeras de Python (`python:3.11-slim`), con comandos de inicio que instalan dependencias y ejecutan las aplicaciones de forma dinámica.

### 1.2 Ejecución básica

Para iniciar todos los servicios por defecto:
```bash
docker-compose up -d
```

Para levantar un servicio específico junto con sus dependencias (ej. PostgreSQL):
```bash
docker-compose up -d servicio-usuarios
```

## 2. Empaquetado para producción (Dockerfiles)

(Nota: En el estado actual del repositorio, las construcciones de imágenes de producción personalizadas están en desarrollo. El archivo docker-compose actual usa comandos `sh -c` para instalar dependencias al vuelo, ideal para desarrollo).

Para desplegar en clústeres como Amazon ECS, cada microservicio debe contar con un archivo `Dockerfile` en su raíz (ej. `backend/servicios/servicio-usuarios/Dockerfile`) que copie el código fuente, instale dependencias de `requirements.txt` y exponga el puerto respectivo usando un servidor WSGI productivo como Gunicorn en lugar del servidor de desarrollo de Flask.
