# Archivo: local-iot.ps1
# Descripción: Script de arranque unificado para el Módulo 5 (Servicios Inteligentes e IoT).
# Módulo: Scripts

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$serviceDir = Join-Path $repoRoot "backend\servicios\servicio-inteligencia-iot"
$venvPython = Join-Path $serviceDir "venv\Scripts\python.exe"

Set-Location $serviceDir

# Verificar e instalar entorno virtual local si no existe
if (-not (Test-Path $venvPython)) {
    Write-Host "Creando entorno virtual de Python para el Módulo 5..." -ForegroundColor Cyan
    python -m venv venv
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt
}

# Configuración de variables de entorno locales
$env:PORT = "5005"
$env:AWS_REGION = "us-east-1"
$env:DYNAMODB_TABLE_LECTURAS_IOT = "lecturas_iot"

# 1. Iniciar Flask API en segundo plano
Write-Host "[Módulo 5] Iniciando Flask API (Analítica e IoT) en puerto 5005..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath $venvPython -ArgumentList "aplicacion.py"

# 2. Iniciar WebSocket Server en primer plano
Write-Host "[Módulo 5] Iniciando WebSocket Server (Telemetría) en puerto 5006..." -ForegroundColor Green
Set-Location telemetria
& $venvPython ejecutar.py
