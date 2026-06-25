# Archivo: local-citas.ps1
# Descripción: Script de automatización de tareas y despliegue.
# Módulo: Scripts

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$serviceDir = Join-Path $repoRoot "backend\servicios\servicio-citas"
$venvPython = Join-Path $serviceDir "venv\Scripts\python.exe"

Set-Location $serviceDir

if (-not (Test-Path $venvPython)) {
    Write-Host "Creando entorno virtual de Python para citas..."
    python -m venv venv
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt
}

$dbPath = Join-Path $repoRoot "backend\servicios\servicio-usuarios\instance\datos_local.db"
$dbUrl = "sqlite:///" + $dbPath.Replace('\', '/')
$env:DATABASE_URL = $dbUrl
$env:DB_SCHEMA = ""
$env:SECRET_KEY = "change_this_secret_at_least_32_chars"
$env:JWT_SECRET_KEY = "change_this_jwt_secret_at_least_32_chars"
$env:PORT = "5002"

Write-Host "Inicializando base de datos de citas..."
& $venvPython datos_iniciales.py

Write-Host "Iniciando servicio de citas en puerto 5002..."
& $venvPython ejecutar.py
