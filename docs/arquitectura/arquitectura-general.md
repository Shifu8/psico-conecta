# Arquitectura general

Descripción corta:
Este documento explica la arquitectura general de PsicoConecta, describiendo la separación por microservicios, las tecnologías principales empleadas y la relación básica entre frontend, servicios backend y bases de datos.

## 1. Descripción de la plataforma

PsicoConecta es una plataforma cloud diseñada para conectar a pacientes y profesionales de la psicología. Su objetivo principal es facilitar la gestión de terapias, ofreciendo herramientas para programar citas, realizar teleconsultas, procesar pagos y, en un futuro, integrar inteligencia IoT para el análisis de emociones y lecturas biométricas.

## 2. Arquitectura y tecnologías base

El proyecto está estructurado como un monorepo de microservicios, donde cada dominio se encapsula en un servicio independiente.

### 2.1 Tecnologías principales

*   **Frontend**: React y Vite, estilizado con TailwindCSS y animaciones con Framer Motion.
*   **Backend**: Python con el microframework Flask.
*   **Base de datos relacional**: PostgreSQL con esquemas separados de forma lógica para usuarios, citas, teleconsulta y pagos.
*   **Base de datos NoSQL / IoT**: DynamoDB para tablas de emociones, lecturas, notificaciones y logs.
*   **Autenticación**: JWT local y Google OAuth directo integrado en Flask.
*   **Recuperación de contraseñas**: Integración con Gmail API.
*   **Infraestructura y despliegue**: AWS (S3, CloudFront, ECR, ECS) con despliegue continuo (CI/CD) vía GitHub Actions.
*   **Integraciones de terceros**: Zoom API para teleconsulta y Stripe Sandbox para pagos.

## 3. Distribución de microservicios y puertos locales

Cada servicio tiene un puerto asignado en el entorno de desarrollo local:

*   **Frontend React**: Puerto `5173`
*   **Puerta de enlace API / Gateway**: Puerto `5000` (Enrutamiento base)
*   **Servicio de Usuarios**: Puerto `5001`
*   **Servicio de Citas**: Puerto `5002`
*   **Servicio de Teleconsulta**: Puerto `5003`
*   **Servicio de Pagos**: Puerto `5004`
*   **Servicio de Inteligencia e IoT**: Puerto `5005`

## 4. Estado actual de los módulos funcionales

Dado que la aplicación es modular, algunos servicios se encuentran totalmente implementados y otros cuentan con la estructura base.

### 4.1 Módulos completamente funcionales

*   **Frontend**: Interfaz de usuario responsiva con soporte para modo claro y oscuro.
*   **Servicio de Usuarios (Gestión de Identidad)**: 
    *   Registro e inicio de sesión.
    *   Autenticación mediante JWT e inicio de sesión con Google OAuth.
    *   Control de acceso basado en roles (Administrador, Psicólogo, Paciente).
    *   Recuperación de contraseña vía Gmail API.
    *   Administración de usuarios y roles.

### 4.2 Módulos en fase estructural

Estos servicios tienen la estructura base y conexión a bases de datos listas, pero requieren exponer lógica de negocio completa:

*   **Servicio de Citas**: Estructura en PostgreSQL (`citas_schema`).
*   **Servicio de Teleconsulta**: Integración con Zoom API.
*   **Servicio de Pagos**: Integración con Stripe Sandbox.
*   **Servicio de Inteligencia e IoT**: Conexión a DynamoDB y AWS IoT Core.

## 5. Funcionamiento general

*   **Desarrollo local**: Preferiblemente mediante Docker Compose, lo cual inicializa PostgreSQL y el backend de usuarios junto con datos de prueba, permitiendo la conexión del frontend de forma fluida.
*   **Entorno de producción**: En AWS se exige HTTPS usando CloudFront, se administra seguridad con AWS Secrets Manager y se validan formularios mediante Cloudflare Turnstile.
*   **Flujo de autenticación**: El frontend obtiene un Token ID de proveedores de identidad, el backend de Flask valida dicho token y gestiona la sesión emitiendo un JWT interno.
