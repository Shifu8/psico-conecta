# Configuración de entorno

Descripción corta:
Este documento proporciona las directrices necesarias para preparar el entorno de trabajo antes de ejecutar PsicoConecta, indicando las herramientas y dependencias que deben estar instaladas en el sistema.

## 1. Requisitos previos (Host)

Para trabajar de forma fluida con el proyecto, tu máquina debe contar con las siguientes herramientas:

- **Git:** Para clonar el repositorio y control de versiones.
- **Node.js (v18 o superior):** Requerido para instalar dependencias y compilar el frontend basado en React y Vite.
- **Python (3.11+):** Requerido si planeas ejecutar los microservicios de forma nativa sin Docker.
- **Docker y Docker Compose:** (Recomendado) Para levantar la base de datos PostgreSQL y los servicios backend de manera unificada sin contaminar el entorno local.
- **PowerShell o Bash:** Para ejecutar los scripts ubicados en la carpeta `scripts/`.

## 2. Pasos iniciales de configuración

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Shifu8/psico-conecta.git
   cd psico-conecta
   ```

2. **Configuración de Variables de Entorno:**
   El proyecto hace uso intensivo de variables de entorno (archivos `.env`) para evitar exponer credenciales. Debes crear los archivos correspondientes a partir de los `.env.example` proporcionados en las carpetas principales. Revisa el documento `variables-entorno.md` para más detalles.

3. **Verificación de puertos:**
   Asegúrate de que los puertos `5173`, `5432` y el rango de `5000` a `5005` estén libres en tu máquina, ya que los microservicios y la base de datos local los utilizarán.
