# Monitoreo SaaS con AWS CloudWatch y PostHog

## Recomendacion

Para infraestructura en AWS usa **Amazon CloudWatch** como base: metricas, logs, alarmas y dashboards. Para actividad de producto y comportamiento de usuarios usa **PostHog** integrado en el frontend; en paralelo, PsicoConecta ahora guarda una **bitacora interna de auditoria** en el backend para registros, inicios de sesion y cambios administrativos.

Elegi PostHog frente a Mixpanel porque encaja mejor con este proyecto: es open source, permite cloud o self-host, tiene analitica de producto, session replay y feature flags. Mixpanel tambien es fuerte en analitica, pero PostHog da mas opciones si luego quieren controlar datos sensibles o moverlo a una instalacion propia.

## Lo que quedo implementado en la app

- Backend: tabla `eventos_auditoria` para eventos de autenticacion y administracion.
- Backend: endpoints admin `GET /api/usuarios/auditoria/resumen` y `GET /api/usuarios/auditoria/eventos`.
- Frontend: panel admin con metricas de inicios exitosos, fallidos, registros, cambios administrativos, tendencia de 7 dias y ultimos eventos.
- Frontend: integracion PostHog opcional con `VITE_POSTHOG_KEY` y `VITE_POSTHOG_HOST`.
- PostgreSQL: migracion lista en `infraestructura/postgres/migracion_eventos_auditoria.sql`.

## Configurar PostHog

1. Crear proyecto en PostHog Cloud o en una instancia self-hosted.
2. Copiar la Project API Key.
3. En `frontend/.env.development` o variables de despliegue:

```env
VITE_POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxx
VITE_POSTHOG_HOST=https://us.i.posthog.com
```

4. Ejecutar el frontend. Si la key esta vacia, la analitica se desactiva sin afectar la app.
5. En PostHog crea dashboards con estos eventos:
   - `inicio_sesion_exitoso`
   - `inicio_google_exitoso`
   - `registro_usuario`
   - `cierre_sesion`
   - `admin_usuario_estado_actualizado`
   - `admin_usuario_editado`
   - `admin_usuario_desactivado`

## Configurar CloudWatch en AWS

La infraestructura del repositorio ya usa ECS/Fargate, ECR, CloudWatch Logs y grupos `/ecs/psicoconecta-*`. Para completar el monitoreo:

1. Verifica que los servicios ECS usen `awslogs` en cada task definition.
2. Crea un tema SNS para alertas y suscribe tu correo.
3. Crea alarmas de CPU y memoria por cada servicio ECS.
4. Crea metric filters sobre CloudWatch Logs para detectar `ERROR`, `Exception`, `Traceback` y `CRITICAL`.
5. Si usas ALB, agrega alarmas de `HTTPCode_ELB_5XX_Count` y `TargetResponseTime`.
6. Si usas RDS PostgreSQL, agrega alarmas para CPU, conexiones, espacio libre y latencia.
7. Activa CloudWatch Container Insights para ver tareas, servicios y cluster ECS con mas detalle.
8. Crea un dashboard CloudWatch para explicar el estado de la infraestructura.

Script listo:

```powershell
.\infraestructura\aws\configurar-monitoreo-cloudwatch.ps1 `
  -Region us-east-2 `
  -Cluster psicoconecta `
  -EmailAlertas tu-correo@dominio.com
```

Si ya tienes el nombre completo del ALB y Target Group:

```powershell
.\infraestructura\aws\configurar-monitoreo-cloudwatch.ps1 `
  -Region us-east-2 `
  -Cluster psicoconecta `
  -EmailAlertas tu-correo@dominio.com `
  -LoadBalancerFullName "app/mi-alb/abc123" `
  -TargetGroupFullName "targetgroup/mi-tg/def456"
```

## Evidencia para la actividad

- Infraestructura: captura de CloudWatch Dashboard `PsicoConecta-Infraestructura`.
- Logs: captura de CloudWatch Logs por servicio, por ejemplo `/ecs/psicoconecta-usuarios`.
- Alertas: captura de CloudWatch Alarms en estado OK o ALARM.
- App: captura del panel admin en `/administrador`, seccion `Seguridad`.
- Producto: captura de dashboard PostHog con eventos de login, registro y administracion.

## Fuentes oficiales

- AWS CloudWatch: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html
- CloudWatch Agent: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html
- CloudWatch Alarms: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Alarms.html
- PostHog React: https://posthog.com/docs/libraries/react
- Mixpanel JavaScript SDK: https://docs.mixpanel.com/docs/tracking-methods/sdks/javascript
