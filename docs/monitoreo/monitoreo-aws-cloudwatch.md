# Monitoreo SaaS con AWS CloudWatch y PostHog

Descripción corta:
Este documento detalla la configuración técnica para integrar PostHog en el frontend para análisis de producto y AWS CloudWatch en el backend para monitoreo de infraestructura y recolección de logs.

## 1. Recomendación de herramientas

Para la infraestructura en AWS, se recomienda utilizar **Amazon CloudWatch** como base central: métricas, logs, alarmas y dashboards.
Para el seguimiento de la actividad de producto y el comportamiento de los usuarios, se recomienda **PostHog** integrado en el frontend. De forma paralela, PsicoConecta guarda una bitácora interna de auditoría en el backend para llevar registro de los inicios de sesión y los cambios administrativos.

PostHog ha sido seleccionado por ser de código abierto, lo que permite su uso en la nube (Cloud) o auto-hospedado (Self-Hosted), e incluye analítica de producto, grabación de sesiones y feature flags, brindando mayores opciones de privacidad.

## 2. Implementación actual

*   **Backend:** Tabla `eventos_auditoria` para registro de eventos críticos.
*   **Backend:** Endpoints administrativos `GET /api/usuarios/auditoria/resumen` y `GET /api/usuarios/auditoria/eventos`.
*   **Frontend:** Panel administrativo que muestra métricas de inicios exitosos, fallidos, registros y tendencias de los últimos 7 días.
*   **Frontend:** Integración de PostHog manejada de forma opcional mediante las variables `VITE_POSTHOG_KEY` y `VITE_POSTHOG_HOST`.

## 3. Configuración de PostHog

1.  Crear un proyecto en PostHog (Cloud o auto-hospedado).
2.  Copiar la *Project API Key*.
3.  Agregar al archivo `.env` del frontend:
    ```env
    VITE_POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxx
    VITE_POSTHOG_HOST=https://us.i.posthog.com
    ```
4.  Si la clave está vacía, la herramienta se desactiva sin afectar el flujo normal de la aplicación.
5.  Eventos clave para configurar dashboards: `inicio_sesion_exitoso`, `inicio_google_exitoso`, `registro_usuario`, `cierre_sesion`, `admin_usuario_estado_actualizado`, `admin_usuario_editado`, `admin_usuario_desactivado`.

## 4. Configurar CloudWatch en AWS

La infraestructura basada en ECS/Fargate y ECR genera registros bajo los grupos `/ecs/psicoconecta-*`.

1.  Verificar que las definiciones de tareas (Task Definitions) de ECS usen `awslogs`.
2.  Crear un tema en SNS para alertas por correo.
3.  Crear alarmas de CPU y memoria por cada servicio ECS.
4.  Definir filtros de métricas (Metric Filters) sobre CloudWatch Logs para detectar cadenas como `ERROR`, `Exception`, y `CRITICAL`.
5.  Si se utiliza Amazon RDS, agregar alarmas de CPU, almacenamiento libre y conexiones.

### 4.1 Script de automatización

Existe un script en el proyecto para automatizar parte del proceso de CloudWatch:

```powershell
.\infraestructura\aws\configurar-monitoreo-cloudwatch.ps1 `
  -Region us-east-2 `
  -Cluster psicoconecta `
  -EmailAlertas tu-correo@dominio.com
```
