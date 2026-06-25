# Instalación y ejecución local

Descripción corta:
Este documento describe de forma breve y clara las opciones disponibles para instalar y ejecutar el proyecto PsicoConecta de forma local en entornos de desarrollo, ya sea usando contenedores Docker o de forma nativa mediante scripts.

## 1. Instrucciones generales de arranque

Para ejecutar la aplicación localmente, el proyecto ofrece un par de maneras. Aquí tienes las dos opciones principales:

## 2. Opción 1: Ejecución nativa (Scripts y SQLite)

Esta es la forma más sencilla si no deseas usar Docker. Utiliza SQLite como base de datos local temporal y levanta los servicios usando unos scripts preparados de PowerShell.

1. **Backend**: Abre una terminal en la raíz del proyecto y ejecuta el script del backend:
   ```powershell
   .\scripts\local-backend.ps1
   ```
   *(Si SQLite queda en un estado inconsistente por algún error anterior, es posible reiniciarlo usando `.\scripts\local-backend.ps1 -Reset`)*

2. **Frontend**: Abre una segunda terminal en la misma carpeta raíz y ejecuta el script del frontend:
   ```powershell
   .\scripts\local-frontend.ps1
   ```

3. **Verificación**: Abre el navegador y visita `http://localhost:5173`.

## 3. Opción 2: Ejecución recomendada (Docker y PostgreSQL)

Esta opción utiliza Docker Compose para levantar PostgreSQL junto con los microservicios del backend, lo cual representa un entorno más similar a producción. Docker también ejecuta el llenado inicial de datos (seed) de forma automática.

1. **Backend y Base de Datos**: Abre una terminal en la raíz del proyecto y levanta el servicio principal:
   ```powershell
   docker-compose up servicio-usuarios
   ```

2. **Frontend**: Abre una segunda terminal, dirígete a la carpeta del frontend y levanta la aplicación de React:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

3. **Verificación**: Abre el navegador y visita `http://localhost:5173`.

## 4. Credenciales de prueba

Para cualquiera de las opciones de ejecución, una vez que la aplicación esté corriendo, es posible probarla usando estas credenciales de prueba preconfiguradas:

- **Administrador:** `admin@psicoconecta.com` (Contraseña: `Admin123*`)
- **Psicólogo:** `psicologo@psicoconecta.com` (Contraseña: `Psicologo123*`)
- **Paciente:** `paciente@psicoconecta.com` (Contraseña: `Paciente123*`)
