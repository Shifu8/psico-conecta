# Frontend PsicoConecta

## Descripción Técnica

El frontend de PsicoConecta es una Single Page Application (SPA) moderna, diseñada para ofrecer una interfaz de usuario fluida, rápida y responsiva para pacientes, profesionales y administradores. Se encarga de toda la interacción visual y la comunicación con los microservicios del backend a través de la Puerta de Enlace API.

## Arquitectura

La aplicación está construida utilizando:
*   **React:** Biblioteca principal para la construcción de la interfaz.
*   **Vite:** Herramienta de construcción y servidor de desarrollo extremadamente rápido.
*   **Tailwind CSS:** Framework de CSS utilitario para un diseño rápido y consistente.
*   **Framer Motion:** Biblioteca para animaciones complejas e interacciones suaves.
*   **React Router:** Para la navegación y enrutamiento del lado del cliente.
*   **@react-oauth/google:** Para la integración de inicio de sesión de Google (SSO).

Se comunica con el backend consumiendo APIs RESTful y gestionando el estado de la sesión, manejando tanto tokens JWT como validaciones de CAPTCHA (Turnstile) cuando corresponde.

## Microservicios Relacionados

*   **Puerta de Enlace API:** El frontend dirige todas sus peticiones (rutas bajo `/api/*`) a la Puerta de Enlace, quien se encarga de distribuirlas.
*   **Servicio de Usuarios:** Para autenticación, registro, perfiles y recuperación de contraseñas.

## Requisitos Previos

*   Node.js (versión 20 LTS o superior).
*   NPM (incluido con Node.js).

## Instalación y Configuración

1.  **Dependencias:**
    Ejecutar dentro del directorio `frontend/`:
    ```bash
    npm install
    ```

2.  **Variables de Entorno:**
    El proyecto utiliza archivos `.env`. Para desarrollo, verifica o ajusta `.env.development`.
    Variables clave:
    *   `VITE_API_URL`: URL base de la API (ej. `http://localhost:5001` localmente o la URL del API Gateway/ALB en producción).
    *   `VITE_GOOGLE_CLIENT_ID`: ID del cliente OAuth de Google.
    *   `VITE_TURNSTILE_SITE_KEY`: Clave de sitio para el CAPTCHA de Cloudflare.

## Ejecución Local

Para ejecutar el servidor de desarrollo con Vite:

```bash
npm run dev
```
La aplicación estará disponible típicamente en `http://localhost:5173`.

## Construcción para Producción

Para compilar y empaquetar la aplicación para producción:

```bash
npm run build
```
Esto generará los archivos estáticos optimizados en el directorio `dist/`, listos para ser servidos por Nginx, S3, CloudFront o cualquier servidor web estático.
