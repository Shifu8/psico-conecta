$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$serviceDir = Join-Path $repoRoot "backend\servicios\servicio-usuarios"
$venvPython = Join-Path $serviceDir "venv\Scripts\python.exe"

Set-Location $serviceDir

if (-not (Test-Path $venvPython)) {
    Write-Host "Creando entorno virtual de Python..."
    python -m venv venv
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt
}

$env:DATABASE_URL = "sqlite:///datos_local.db"
$env:DATABASE_SCHEMA = ""
$env:SECRET_KEY = "change_this_secret_at_least_32_chars"
$env:JWT_SECRET_KEY = "change_this_jwt_secret_at_least_32_chars"
$env:MODO_DESARROLLO = "true"
$env:FRONTEND_URL = "http://localhost:5173"
$env:CORS_ORIGINS = "http://localhost:5173"

& $venvPython datos_iniciales.py
& $venvPython ejecutar.py
