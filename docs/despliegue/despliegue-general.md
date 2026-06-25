# Despliegue general

Descripción corta:
Este documento describe de forma breve y clara la estrategia general de despliegue y promoción de código para la plataforma PsicoConecta desde desarrollo hasta producción.

## 1. Estrategia de despliegue

PsicoConecta adopta un enfoque de despliegue continuo (CI/CD) diseñado para facilitar actualizaciones rápidas e independientes para cada microservicio y para el frontend.

### 1.1 División por capas

*   **Frontend**: Aplicación de una sola página (SPA) construida y empaquetada como archivos estáticos. Se despliega típicamente en redes de distribución de contenido (CDN) como AWS CloudFront respaldado por S3.
*   **Backend (Microservicios)**: Cada microservicio es contenerizado o empaquetado y se despliega como una entidad separada. Esto puede realizarse mediante plataformas como AWS Elastic Beanstalk, o clústeres de contenedores como Amazon ECS.
*   **Bases de Datos**: Administradas fuera del ciclo de vida de las aplicaciones, típicamente utilizando servicios gestionados (ej. Amazon RDS para PostgreSQL, Amazon DynamoDB para IoT/NoSQL).

## 2. Herramientas de automatización

El proyecto cuenta con un script principal de despliegue (ubicado en `scripts/despliegue.sh`) que automatiza el proceso de empaquetado y subida a los servicios de AWS utilizando AWS CLI. Se recomienda no ejecutar subidas manuales directas, sino utilizar estos scripts o integrarlos en flujos de trabajo de GitHub Actions.

## 3. Ambientes

*   **Desarrollo Local**: Utilizando Docker Compose (`docker-compose.yml`) para levantar todos los servicios y probar la interconectividad.
*   **Staging/Testing**: (Pendiente de documentar implementación) Entorno espejo a producción con datos de prueba.
*   **Producción**: Entorno público con dominios seguros (HTTPS), protección WAF y bases de datos gestionadas de alta disponibilidad.
