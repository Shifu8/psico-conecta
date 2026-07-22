# Archivo: build-and-push-all.ps1
# Descripción: Construye y sube las imágenes Docker de todos los microservicios a AWS ECR.

$ACCOUNT_ID = $(aws sts get-caller-identity --query Account --output text)
$REGION = "us-east-2"

Write-Host "=== INICIANDO SESION EN ECR ($ACCOUNT_ID) ===" -ForegroundColor Green
$password = aws ecr get-login-password --region $REGION
wsl -d Ubuntu-22.04 -u root -- sh -c "echo $password | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

$SERVICIOS = @(
    @{name="puerta-enlace"; dockerfile="backend/puerta-enlace-api/Dockerfile"},
    @{name="usuarios"; dockerfile="backend/servicios/servicio-usuarios/Dockerfile"},
    @{name="citas"; dockerfile="backend/servicios/servicio-citas/Dockerfile"},
    @{name="teleconsulta"; dockerfile="backend/servicios/servicio-teleconsulta/Dockerfile"},
    @{name="pagos"; dockerfile="backend/servicios/servicio-pagos/Dockerfile"},
    @{name="iot"; dockerfile="backend/servicios/servicio-inteligencia-iot/Dockerfile"}
)

$wslRepoPath = "/mnt/c/Users/andre/OneDrive/Desktop/psico-conecta"

foreach ($svc in $SERVICIOS) {
    $REPO = "psicoconecta/$($svc.name)"
    $URI = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO"

    Write-Host "`nConstruyendo $($svc.name) en WSL..." -ForegroundColor Yellow
    wsl -d Ubuntu-22.04 -u root -- sh -c "cd $wslRepoPath && docker build -t $REPO -f $($svc.dockerfile) ."
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error al construir $($svc.name)" -ForegroundColor Red
        exit 1
    }

    Write-Host "Subiendo $($svc.name) a ECR..." -ForegroundColor Yellow
    wsl -d Ubuntu-22.04 -u root -- sh -c "docker tag ${REPO}:latest ${URI}:latest && docker push ${URI}:latest"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  - $URI:latest subida con exito!" -ForegroundColor Green
    } else {
        Write-Host "Error al subir $($svc.name)" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "TODAS LAS IMAGENES SUBIDAS A ECR EXITOSAMENTE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
