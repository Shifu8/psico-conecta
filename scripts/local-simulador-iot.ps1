# Archivo: local-simulador-iot.ps1
# Descripción: Script de arranque del simulador ESP32 de telemetría e IoT.
# Módulo: Scripts

param(
    [string]$PatientId = "4",
    [int]$Duracion = 15
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$simuladorDir = Join-Path $repoRoot "backend\servicios\servicio-inteligencia-iot\simulador"
$venvPython = Join-Path $repoRoot "backend\servicios\servicio-inteligencia-iot\venv\Scripts\python.exe"

Set-Location $simuladorDir

if (-not (Test-Path $venvPython)) {
    Write-Host "Ejecutando con Python global..." -ForegroundColor Yellow
    python simulador_esp32.py $PatientId $Duracion
} else {
    Write-Host "Ejecutando simulador ESP32 con entorno virtual..." -ForegroundColor Green
    & $venvPython simulador_esp32.py $PatientId $Duracion
}
