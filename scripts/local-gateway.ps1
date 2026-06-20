$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$serviceDir = Join-Path $repoRoot "backend\puerta-enlace-api"
$venvPython = Join-Path $serviceDir "venv\Scripts\python.exe"

Set-Location $serviceDir

if (-not (Test-Path $venvPython)) {
    Write-Host "Creando entorno virtual de Python para gateway..."
    python -m venv venv
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt
}

$env:PORT = "5000"
$env:USUARIOS_SERVICE_URL = "http://127.0.0.1:5001"
$env:CITAS_SERVICE_URL = "http://127.0.0.1:5002"

Write-Host "Iniciando API Gateway en puerto 5000..."
& $venvPython aplicacion.py
