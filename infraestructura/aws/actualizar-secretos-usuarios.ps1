# Archivo: actualizar-secretos-usuarios.ps1
# Descripción: Script de automatización de tareas y despliegue.
# Módulo: Infraestructura

param(
    [string]$Region = "us-east-2",
    [string]$EnvPath = "backend/servicios/servicio-usuarios/.env"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $EnvPath)) {
    throw "No se encontro el archivo $EnvPath"
}

function Leer-Env {
    param([string]$Ruta)
    $valores = @{}
    Get-Content $Ruta | ForEach-Object {
        if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
        $partes = $_ -split '=', 2
        $clave = $partes[0].Trim()
        $valor = $partes[1].Trim()
        if ($clave) { $valores[$clave] = $valor }
    }
    return $valores
}

function Actualizar-Secreto {
    param(
        [string]$Nombre,
        [string]$Valor
    )
    if ([string]::IsNullOrWhiteSpace($Valor)) {
        Write-Host "Saltando $Nombre porque no tiene valor." -ForegroundColor Yellow
        return
    }

    $oldAction = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    $existe = $null
    $existe = aws secretsmanager describe-secret --secret-id $Nombre --region $Region --query ARN --output text 2>$null
    $ErrorActionPreference = $oldAction

    if ($LASTEXITCODE -eq 0 -and $existe -and $existe -ne "None") {
        aws secretsmanager put-secret-value --secret-id $Nombre --secret-string $Valor --region $Region | Out-Null
        Write-Host "Actualizado $Nombre" -ForegroundColor Green
    } else {
        $error.Clear()
        aws secretsmanager create-secret --name $Nombre --secret-string $Valor --region $Region | Out-Null
        Write-Host "Creado $Nombre" -ForegroundColor Green
    }
}

$valoresEnv = Leer-Env -Ruta $EnvPath
$requeridos = @(
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "GOOGLE_SENDER_EMAIL",
    "TURNSTILE_SECRET_KEY"
)

foreach ($clave in $requeridos) {
    Actualizar-Secreto -Nombre "psicoconecta/$clave" -Valor $valoresEnv[$clave]
}

Write-Host ""
Write-Host "Secretos de usuarios listos para ECS." -ForegroundColor Cyan
