# Archivo: add_headers_v2.py
# Descripción: Módulo de lógica de negocio, rutas o configuración.
# Módulo: Proyecto General

import os

EXCLUDE_DIRS = {
    "node_modules", "venv", "env", "__pycache__", "dist", "build", 
    ".git", ".pytest_cache", ".wrangler", ".agents", ".qodo", "instance", "migrations", "frontend"
}

ALLOWED_EXTENSIONS = {
    ".py", ".sh", ".ps1", ".bat"
}

def get_module_name(path):
    path_str = path.replace("\\", "/").lower()
    if "servicio-usuarios" in path_str: return "Servicio Usuarios"
    if "servicio-citas" in path_str: return "Servicio Citas"
    if "servicio-teleconsulta" in path_str: return "Servicio Teleconsultas"
    if "servicio-pagos" in path_str: return "Servicio Pagos"
    if "servicio-inteligencia-iot" in path_str: return "Servicio IoT"
    if "puerta-enlace-api" in path_str: return "Puerta de Enlace"
    if "scripts" in path_str: return "Scripts"
    if "infraestructura" in path_str: return "Infraestructura"
    return "Proyecto General"

def get_description(filename, ext):
    if filename == "aplicacion.py": return "Punto de entrada principal e inicialización del servidor."
    if filename == "datos_iniciales.py": return "Poblado de datos iniciales para la base de datos."
    if filename == "ejecutar.py": return "Inicialización y ejecución del servidor de la API."
    if filename == "setup_google_credentials.py": return "Configuración para credenciales de Google API."
    if filename == "Dockerfile": return "Receta de construcción de contenedor Docker."
    if ext == ".ps1" or ext == ".sh" or ext == ".bat": return "Script de automatización de tareas y despliegue."
    if ext == ".py": return "Módulo de lógica de negocio, rutas o configuración."
    return "Archivo funcional del módulo."

def process_file(filepath):
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in ALLOWED_EXTENSIONS and filename != "Dockerfile":
        return
        
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    # Evitar duplicados
    if "Archivo:" in content[:200] and "Descripción:" in content[:200]:
        return

    module_name = get_module_name(filepath)
    desc = get_description(filename, ext)
    
    if ext in (".py", ".sh", ".ps1", ".bat") or filename == "Dockerfile":
        header = f"# Archivo: {filename}\n# Descripción: {desc}\n# Módulo: {module_name}\n\n"
    else:
        return

    lines = content.split('\n')
    if len(lines) > 0 and (lines[0].startswith("#!") or 'coding:' in lines[0] or '-*-' in lines[0]):
        new_content = lines[0] + '\n\n' + header + '\n'.join(lines[1:])
    else:
        new_content = header + content

    try:
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")
    except Exception as e:
        print(f"Error writing {filepath}: {e}")

def main():
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for file in files:
            filepath = os.path.join(root, file)
            process_file(filepath)

if __name__ == "__main__":
    main()
