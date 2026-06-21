# Instrucciones de Arranque para PsicoConecta

Para ejecutar la aplicación localmente, el proyecto ofrece un par de maneras. Aquí tienes las dos opciones principales:

## Opción 1: La más rápida (Usando los scripts y SQLite)
Esta es la forma más sencilla si no quieres usar Docker. Utiliza SQLite como base de datos local y levanta los servicios usando unos scripts preparados.

1. **Abre una terminal en la raíz del proyecto** y ejecuta el script del backend:
   ```powershell
   .\scripts\local-backend.ps1
   ```
   *(Si SQLite quedó a medias por algún error anterior, puedes reiniciarlo usando `.\scripts\local-backend.ps1 -Reset`)*

2. **Abre una segunda terminal** en la misma carpeta raíz y ejecuta el script del frontend:
   ```powershell
   .\scripts\local-frontend.ps1
   ```

3. Abre tu navegador y ve a: **http://localhost:5173**

---

## Opción 2: Recomendada (Docker para la BD + Frontend manual)
Esta opción utiliza Docker para levantar PostgreSQL junto con el backend, lo cual es más cercano a un entorno real. Docker también ejecuta el llenado inicial de datos (seed) de forma automática.

1. **Abre una terminal en la raíz del proyecto** y levanta el servicio de usuarios (esto iniciará también PostgreSQL):
   ```powershell
   docker compose up servicio-usuarios
   ```

2. **Abre una segunda terminal**, ve a la carpeta del frontend y levántalo:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

3. Abre tu navegador y ve a: **http://localhost:5173**

---

## Credenciales de prueba
Para cualquiera de las dos opciones, una vez que la aplicación esté corriendo, podrás probarla usando estas credenciales preconfiguradas:

- **Administrador:** `admin@psicoconecta.com` (Contraseña: `Admin123*`)
- **Psicólogo:** `psicologo@psicoconecta.com` (Contraseña: `Psicologo123*`)
- **Paciente:** `paciente@psicoconecta.com` (Contraseña: `Paciente123*`)
