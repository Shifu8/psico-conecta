$ACCOUNT_ID = $(aws sts get-caller-identity --query Account --output text)
$REGION = "us-east-2"

Write-Host "=== BUILD Y PUSH A ECR ===" -ForegroundColor Green

$SERVICIOS = @(
    @{name="puerta-enlace"; dockerfile="backend/puerta-enlace-api/Dockerfile"},
    @{name="usuarios"; dockerfile="backend/servicios/servicio-usuarios/Dockerfile"},
    @{name="citas"; dockerfile="backend/servicios/servicio-citas/Dockerfile"},
    @{name="teleconsulta"; dockerfile="backend/servicios/servicio-teleconsulta/Dockerfile"},
    @{name="pagos"; dockerfile="backend/servicios/servicio-pagos/Dockerfile"},
    @{name="iot"; dockerfile="backend/servicios/servicio-inteligencia-iot/Dockerfile"}
)

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

foreach ($svc in $SERVICIOS) {
    $REPO = "psicoconecta/$($svc.name)"
    $URI = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO"

    Write-Host "`nConstruyendo $($svc.name)..." -ForegroundColor Yellow
    docker build -t $REPO -f $($svc.dockerfile) .
    docker tag $REPO:latest "$URI:latest"
    docker push "$URI:latest"

    Write-Host "  - $URI:latest subida" -ForegroundColor Green
}

Write-Host "`n=== TODAS LAS IMAGENES SUBIDAS ===" -ForegroundColor Green
