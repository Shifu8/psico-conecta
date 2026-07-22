# Archivo: local-pagos.ps1
# Descripción: Script de automatización de tareas para el servicio de pagos.
# Módulo: Scripts

param([switch]$Reset)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$serviceDir = Join-Path $repoRoot "backend\servicios\servicio-pagos"
$venvDir = Join-Path $serviceDir "venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

Set-Location $serviceDir

if ($Reset) {
    if (Test-Path $venvDir) { Remove-Item $venvDir -Recurse -Force }
}

if (-not (Test-Path $venvPython)) {
    Write-Host "Creando entorno virtual de Python para pagos..."
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
$env:PORT = "5004"
$env:PAGOS_INTERNAL_TOKEN = "change_this_payments_internal_token"
$env:USERS_SERVICE_URL = "http://127.0.0.1:5001"
$env:CITAS_SERVICE_URL = "http://127.0.0.1:5002"

Write-Host "Inicializando base de datos de pagos..."
& $venvPython preparar_bd.py

Write-Host "Iniciando servicio de pagos en puerto 5004..."
& $venvPython ejecutar.py
