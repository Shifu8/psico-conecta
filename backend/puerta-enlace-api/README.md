# Puerta de Enlace API (API Gateway)

## Descripción Técnica

Este microservicio actúa como un proxy inverso y enrutador principal para la plataforma PsicoConecta. Recibe las peticiones del frontend y las redirige a los microservicios correspondientes del backend basándose en la ruta de la solicitud. Su objetivo principal es abstraer la complejidad de la arquitectura de microservicios, proporcionando un único punto de entrada para los clientes.

## Arquitectura

La Puerta de Enlace está desarrollada en Python utilizando Flask y `requests`. Define reglas predefinidas en un diccionario de configuración que mapean los prefijos de las URL (`/api/usuarios`, `/api/citas`, etc.) hacia las URLs base internas de cada microservicio respectivo (`http://servicio-usuarios:5001`, etc.).

Al recibir una petición, la puerta de enlace extrae el path original, determina el servicio de destino, reenvía la petición completa (incluyendo cabeceras, cuerpo, parámetros, cookies) y devuelve la respuesta exacta producida por el servicio subyacente.

## Microservicios Relacionados

*   **Todos los servicios del backend**: La puerta de enlace delega peticiones a:
    *   Servicio de Usuarios (`/api/usuarios`)
    *   Servicio de Citas (`/api/citas`)
    *   Servicio de Teleconsulta (`/api/teleconsulta`)
    *   Servicio de Pagos (`/api/pagos`)
    *   Servicio de IoT (`/api/iot`)

## Requisitos Previos

*   Python 3.11 o superior.
*   Conectividad de red con los microservicios destino (generalmente administrada vía Docker Compose o la red del clúster).

## Instalación y Configuración

1.  **Entorno Virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: .\venv\Scripts\activate
    ```

2.  **Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Variables de Entorno:**
    Copiar `.env.example` a `.env` y ajustar si es necesario. (Por defecto, asume los nombres de los servicios de Docker).

## Ejecución Local

Para ejecutar el servicio localmente en modo desarrollo:

```bash
python aplicacion.py
```
El servicio estará disponible en el puerto `5000` por defecto.
