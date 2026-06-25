# Estructura del proyecto

Descripción corta:
Este documento describe el árbol de directorios del repositorio PsicoConecta, explicando la finalidad de cada carpeta principal para facilitar la navegación a los desarrolladores.

## 1. Árbol de directorios

```text
psico-conecta/
├── backend/
│   ├── puerta-enlace-api/         # API Gateway (Enrutamiento base)
│   ├── servicios/                 # Contenedor de todos los microservicios backend
│   │   ├── servicio-citas/        # Lógica de agenda y disponibilidad
│   │   ├── servicio-inteligencia-iot/ # Integraciones IoT y DynamoDB
│   │   ├── servicio-pagos/        # Integración con Stripe Sandbox
│   │   ├── servicio-teleconsulta/ # Integración con Zoom API
│   │   └── servicio-usuarios/     # Autenticación, JWT y OAuth
│   ├── compartido/                # Funciones, utilidades y modelos comunes (en desarrollo)
│   └── requirements/              # Dependencias específicas y comunes de Python
├── docs/                          # Documentación técnica del proyecto
│   ├── api/                       # Referencias de endpoints
│   ├── arquitectura/              # Decisiones de diseño y patrones
│   ├── base-datos/                # Esquemas y configuraciones de DB
│   ├── despliegue/                # Instrucciones de subida a la nube
│   ├── instalacion/               # Pasos para arrancar el entorno local
│   ├── monitoreo/                 # Logs, dashboards y métricas
│   └── pruebas/                   # Estrategias de testing
├── frontend/                      # Proyecto React + Vite + TailwindCSS
├── infraestructura/               # Scripts y configuraciones IAC (PostgreSQL, AWS, Cloudflare)
├── scripts/                       # Scripts de automatización y despliegue (ej. despliegue.sh)
├── docker-compose.yml             # Orquestación local de contenedores
└── README.md                      # Documento principal de entrada al proyecto
```

## 2. Decisiones de diseño estructural

1. **Separación de responsabilidades**: Las carpetas `frontend` y `backend` están estrictamente separadas para permitir despliegues aislados (S3/CloudFront para el front, Elastic Beanstalk / ECS para el backend).
2. **Carpeta `servicios/`**: Todos los microservicios se agrupan en este nivel. Renombrarlos internamente requeriría refactorización de scripts de Docker y despliegue.
3. **Carpeta `docs/`**: Centraliza todos los archivos de soporte técnico para que no contaminen la raíz del repositorio y sea más fácil navegar el conocimiento del proyecto.
