# Contexto de PsicoConecta

## ¿De qué trata la aplicación?
PsicoConecta es una plataforma cloud diseñada para conectar a pacientes y profesionales de la psicología. Su objetivo principal es facilitar la gestión de terapias, ofreciendo herramientas para programar citas, realizar teleconsultas, procesar pagos y, en un futuro, integrar inteligencia IoT para el análisis de emociones y lecturas biométricas.

## Arquitectura y Tecnologías
El proyecto está estructurado como un **monorepo de microservicios**.

### Tecnologías principales:
*   **Frontend**: React + Vite, estilizado con TailwindCSS y animaciones con Framer Motion.
*   **Backend**: Python con el microframework Flask.
*   **Base de datos relacional**: PostgreSQL (con una instancia que aloja esquemas separados para usuarios, citas, teleconsulta y pagos).
*   **Base de datos NoSQL / IoT**: DynamoDB (tablas para emociones, lecturas, notificaciones y logs).
*   **Autenticación**: JWT local y Google OAuth directo integrado en Flask.
*   **Recuperación de contraseñas**: Gmail API (sin depender de SMTP tradicional).
*   **Cloud / Despliegue**: AWS (S3, CloudFront, ECR, ECS) con despliegue continuo (CI/CD) vía GitHub Actions.
*   **Integraciones de terceros**: Zoom API (teleconsulta), Stripe Sandbox (pagos).

### Distribución de microservicios y puertos:
*   **Frontend React**: Puerto `5173`
*   **Puerta de enlace API / Gateway**: Puerto `5000` (Enrutamiento y descubrimiento base)
*   **Servicio de Usuarios**: Puerto `5001`
*   **Servicio de Citas**: Puerto `5002`
*   **Servicio de Teleconsulta**: Puerto `5003`
*   **Servicio de Pagos**: Puerto `5004`
*   **Servicio de Inteligencia e IoT**: Puerto `5005`

## Módulos Implementados hasta ahora (Estado Actual)
Dado que la aplicación se encuentra en fase de desarrollo, el nivel de completitud varía según el módulo:

### 1. Módulos Completamente Funcionales:
*   **Frontend**: Interfaz de usuario responsiva, funcional y con soporte para modo claro/oscuro.
*   **Servicio de Usuarios (Gestión de Identidad y Acceso)**: 
    *   Registro e inicio de sesión seguro.
    *   Autenticación mediante JWT.
    *   Inicio de sesión social (Google OAuth).
    *   Control de acceso basado en roles (Administrador, Psicólogo, Paciente).
    *   Recuperación y restablecimiento de contraseña vía Gmail API mediante un token temporal.
    *   Protección de seguridad (límite de intentos de inicio de sesión, validación de entradas).
    *   Administración de usuarios (CRUD y gestión de roles/estados).

### 2. Módulos en Fase de "Esqueleto" (Preparados pero sin lógica completa expuesta):
Estos servicios tienen la estructura base, comunicación enrutada y bases de datos preparadas, pero la lógica de negocio final aún no está expuesta públicamente por razones de seguridad hasta implementar persistencia final y autorización estricta:
*   **Servicio de Citas**: Estructura avanzada preparada en PostgreSQL (`citas_schema`).
*   **Servicio de Teleconsulta**: Integración con Zoom API preparada (`teleconsulta_schema`).
*   **Servicio de Pagos**: Integración con Stripe Sandbox preparada (`pagos_schema`).
*   **Servicio de Inteligencia e IoT**: DynamoDB y AWS IoT Core preparados para el manejo de datos flexibles.

## ¿Cómo funciona el entorno actual?
*   **Desarrollo Local**: Se puede ejecutar localmente usando scripts de PowerShell (con SQLite temporal) o preferiblemente **usando Docker Compose**. Docker levanta la instancia de PostgreSQL y el backend del servicio de usuarios con datos semilla de prueba (demo de Admin, Psicólogo y Paciente). El frontend en Vite se conecta al servicio de usuarios levantado.
*   **Seguridad y Producción**: En producción, se exige HTTPS utilizando CloudFront como origen seguro, y el manejo de secretos se realiza a través de AWS Secrets Manager. Opcionalmente, se integra Cloudflare Turnstile como CAPTCHA para formularios públicos.
*   **Flujo de Datos (Ejemplo Auth Google)**: El frontend mediante la librería `@react-oauth/google` genera un Token ID -> El backend de Flask recibe y verifica el token contra la API de Google y registra/autentica al usuario en la base de datos PostgreSQL de forma transparente.

---
Este documento proporciona una fotografía general del estado actual del monorepo, destacando una base sólida de autenticación e infraestructura sobre la cual se construirán el resto de los módulos funcionales para las terapias y pagos.
