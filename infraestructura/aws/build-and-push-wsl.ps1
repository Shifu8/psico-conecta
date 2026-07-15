# Archivo: build-and-push-wsl.ps1
# Descripción: Script de automatización de tareas y despliegue usando WSL para Docker y PowerShell para AWS CLI.
# Módulo: Infraestructura

$ACCOUNT_ID = $(aws sts get-caller-identity --query Account --output text)
$REGION = "us-east-2"

Write-Host "=== BUILD Y PUSH A ECR USANDO WSL ===" -ForegroundColor Green

# 1. Crear el repositorio de usuarios si no existe
$repoExists = aws ecr describe-repositories --repository-name "psicoconecta/usuarios" --region $REGION --query "repositories[0].repositoryName" --output text 2>$null
if ($LASTEXITCODE -ne 0 -or -not $repoExists -or $repoExists -eq "None") {
    Write-Host "Creando repositorio ECR psicoconecta/usuarios..." -ForegroundColor Yellow
    aws ecr create-repository --repository-name "psicoconecta/usuarios" --region $REGION | Out-Null
}

# 2. Login ECR en WSL
Write-Host "Iniciando sesion en ECR..." -ForegroundColor Yellow
$password = aws ecr get-login-password --region $REGION
wsl -d Ubuntu -- sh -c "echo $password | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

# 3. Construir y subir cada servicio
$SERVICIOS = @(
    @{name="puerta-enlace"; dockerfile="backend/puerta-enlace-api/Dockerfile"},
    @{name="usuarios"; dockerfile="backend/servicios/servicio-usuarios/Dockerfile"},
    @{name="iot"; dockerfile="backend/servicios/servicio-inteligencia-iot/Dockerfile"}
)

foreach ($svc in $SERVICIOS) {
    $REPO = "psicoconecta/$($svc.name)"
    $URI = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO"

    Write-Host "`nConstruyendo $($svc.name) en WSL..." -ForegroundColor Yellow
    wsl -d Ubuntu -- sh -c "cd /home/brandon/psico-conecta && docker build -t $REPO -f $($svc.dockerfile) ."
    
    Write-Host "Tagging and pushing $($svc.name)..." -ForegroundColor Yellow
    wsl -d Ubuntu -- sh -c "docker tag ${REPO}:latest ${URI}:latest && docker push ${URI}:latest"

    Write-Host "  - $URI:latest subida con exito!" -ForegroundColor Green
}

Write-Host "`n=== TODAS LAS IMAGENES SUBIDAS A ECR ===" -ForegroundColor Green
