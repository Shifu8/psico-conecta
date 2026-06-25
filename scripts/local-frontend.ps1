# Archivo: local-frontend.ps1
# Descripción: Script de automatización de tareas y despliegue.
# Módulo: Scripts

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $repoRoot "frontend"

Set-Location $frontendDir

if (-not (Test-Path "node_modules")) {
    npm.cmd install
}

npm.cmd run dev
