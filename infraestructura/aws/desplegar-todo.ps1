param(
    [string]$Region = "us-east-2",
    [string]$Cluster = "psicoconecta",
    [string]$CuentaAWS = "",
    [string]$FrontendBucket = "psicoconecta-frontend-060899556466",
    [string]$GoogleClientId = ""
)

if (-not $CuentaAWS) {
    $CuentaAWS = $(aws sts get-caller-identity --query Account --output text)
}

Write-Host "=== DESPLIEGUE COMPLETO PSICOCONECTA ===" -ForegroundColor Green

# ============================================================
# 0. FIJAR IAM ROLE (permisos para leer Secrets Manager)
# ============================================================
Write-Host "=== 0. FIJANDO IAM ROLE ===" -ForegroundColor Yellow
$roleName = "ecsTaskExecutionRole"
$policyExists = aws iam list-attached-role-policies --role-name $roleName --region $Region --query "AttachedPolicies[?PolicyName=='SecretsManagerReadAccess'].PolicyName" --output text 2>$null
if (-not $policyExists) {
    Write-Host "  Agregando SecretsManagerReadAccess al role..." -ForegroundColor Yellow
    aws iam attach-role-policy --role-name $roleName --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite 2>$null
    # Alternativa: crear inline policy solo para GetSecretValue
    $inlinePolicy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "arn:aws:secretsmanager:us-east-2:*:secret:psicoconecta/*"
        }
    ]
}
"@
    aws iam put-role-policy --role-name $roleName --policy-name psicoconecta-secrets --policy-document $inlinePolicy 2>$null
    Write-Host "  Política psicoconecta-secrets agregada." -ForegroundColor Green
} else {
    Write-Host "  SecretsManagerReadAccess ya existe" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Region: $Region" -ForegroundColor Cyan
Write-Host "Cuenta: $CuentaAWS" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 1. CREAR SECRETS FALTANTES EN SECRETS MANAGER
# ============================================================
Write-Host "=== 1. CREANDO SECRETS ===" -ForegroundColor Yellow

# GOOGLE_CLIENT_SECRET
$secretExists = aws secretsmanager list-secrets --region $Region --query "SecretList[?Name=='psicoconecta/GOOGLE_CLIENT_SECRET'].Name" --output text
if (-not $secretExists) {
    Write-Host "  [!] GOOGLE_CLIENT_SECRET no existe. Crearlo manualmente:" -ForegroundColor Yellow
    Write-Host "  aws secretsmanager create-secret --name psicoconecta/GOOGLE_CLIENT_SECRET --secret-string '{\"GOOGLE_CLIENT_SECRET\":\"<tu-client-secret>\"}' --region $Region" -ForegroundColor Yellow
} else {
    Write-Host "  psicoconecta/GOOGLE_CLIENT_SECRET ya existe" -ForegroundColor Gray
}

# GOOGLE_REFRESH_TOKEN
$secretExists2 = aws secretsmanager list-secrets --region $Region --query "SecretList[?Name=='psicoconecta/GOOGLE_REFRESH_TOKEN'].Name" --output text
if (-not $secretExists2) {
    Write-Host "  [!] GOOGLE_REFRESH_TOKEN no existe. Crealo manualmente:" -ForegroundColor Yellow
    Write-Host "  aws secretsmanager create-secret --name psicoconecta/GOOGLE_REFRESH_TOKEN --secret-string '{\"GOOGLE_REFRESH_TOKEN\":\"<tu-refresh-token>\"}' --region $Region" -ForegroundColor Yellow
} else {
    Write-Host "  psicoconecta/GOOGLE_REFRESH_TOKEN ya existe" -ForegroundColor Gray
}

# Actualizar SECRET_KEY si tiene valor por defecto
$secVal = aws secretsmanager get-secret-value --secret-id psicoconecta/SECRET_KEY --region $Region --query SecretString --output text 2>$null
if ($secVal -and $secVal.Contains("change_this_secret")) {
    Write-Host "  Actualizando SECRET_KEY (tiene valor por defecto)..." -ForegroundColor Yellow
    $newKey = -join ((48..57)+(65..90)+(97..122) | Get-Random -Count 32 | % {[char]$_})
    aws secretsmanager put-secret-value --secret-id psicoconecta/SECRET_KEY --secret-string "{\"SECRET_KEY\":\"$newKey\"}" --region $Region
}

# Actualizar JWT_SECRET_KEY si tiene valor por defecto
$jwtVal = aws secretsmanager get-secret-value --secret-id psicoconecta/JWT_SECRET_KEY --region $Region --query SecretString --output text 2>$null
if ($jwtVal -and $jwtVal.Contains("change_this_jwt_secret")) {
    Write-Host "  Actualizando JWT_SECRET_KEY (tiene valor por defecto)..." -ForegroundColor Yellow
    $newJwt = -join ((48..57)+(65..90)+(97..122) | Get-Random -Count 32 | % {[char]$_})
    aws secretsmanager put-secret-value --secret-id psicoconecta/JWT_SECRET_KEY --secret-string "{\"JWT_SECRET_KEY\":\"$newJwt\"}" --region $Region
}

# ============================================================
# 2. CONSTRUIR Y SUBIR IMAGENES A ECR
# ============================================================
Write-Host "`n=== 2. BUILD & PUSH A ECR ===" -ForegroundColor Yellow

$SERVICIOS_BUILD = @(
    @{name="usuarios"; dockerfile="backend/servicios/servicio-usuarios/Dockerfile"},
    @{name="puerta-enlace"; dockerfile="backend/puerta-enlace-api/Dockerfile"}
)

# Login ECR
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$CuentaAWS.dkr.ecr.$Region.amazonaws.com"

foreach ($svc in $SERVICIOS_BUILD) {
    $REPO = "psicoconecta/$($svc.name)"
    $URI = "$CuentaAWS.dkr.ecr.$Region.amazonaws.com/$REPO"

    Write-Host "  Construyendo y subiendo $($svc.name)..." -ForegroundColor Yellow

    # Asegurar que el repo ECR existe
    aws ecr create-repository --repository-name $REPO --region $Region 2>$null | Out-Null

    docker build -t $REPO -f $($svc.dockerfile) .
    docker tag $REPO:latest "$URI:latest"
    docker push "$URI:latest"

    Write-Host "    $URI:latest subida" -ForegroundColor Green
}

# ============================================================
# 3. REGISTRAR TASK DEFINITIONS
# ============================================================
Write-Host "`n=== 3. REGISTRANDO TASK DEFINITIONS ===" -ForegroundColor Yellow

Get-ChildItem infraestructura/aws/task-definition-*.json | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content.Replace("ACCOUNT_ID", $CuentaAWS)
    Set-Content $_.FullName $content
}

$TASK_DEFS = @(
    "infraestructura/aws/task-definition-usuarios.json",
    "infraestructura/aws/task-definition-puerta-enlace.json"
)

$taskDefArns = @{}
foreach ($td in $TASK_DEFS) {
    Write-Host "  Registrando $td..." -ForegroundColor Yellow
    $arn = aws ecs register-task-definition --cli-input-json file://$td --region $Region --query "taskDefinition.taskDefinitionArn" --output text
    $name = [System.IO.Path]::GetFileNameWithoutExtension($td).Replace("task-definition-","")
    $taskDefArns[$name] = $arn
    Write-Host "    $arn" -ForegroundColor Green
}

# ============================================================
# 4. FIJAR SECURITY GROUP (abrir puertos backend)
# ============================================================
Write-Host "`n=== 4. FIJANDO SECURITY GROUP ===" -ForegroundColor Yellow
$SG_ID = aws ec2 describe-security-groups --group-names psicoconecta-alb-sg --query "SecurityGroups[0].GroupId" --output text --region $Region 2>$null
if ($SG_ID -and $SG_ID -ne "None") {
    $PUERTOS = @(5000, 5001, 5002, 5003, 5004, 5005)
    foreach ($puerto in $PUERTOS) {
        aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port $puerto --cidr 0.0.0.0/0 --region $Region 2>$null
    }
    Write-Host "  Puertos backend abiertos en SG: $SG_ID" -ForegroundColor Green
} else {
    Write-Host "  [!] SG psicoconecta-alb-sg no encontrado, creando..." -ForegroundColor Yellow
    $VPC_ID = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $Region
    $SG_ID = aws ec2 create-security-group --group-name psicoconecta-alb-sg --description "PsicoConecta services" --vpc-id $VPC_ID --region $Region --query "GroupId" --output text
    foreach ($puerto in @(80, 443, 5000, 5001, 5002, 5003, 5004, 5005)) {
        aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port $puerto --cidr 0.0.0.0/0 --region $Region 2>$null
    }
    Write-Host "  SG creado: $SG_ID" -ForegroundColor Green
}

# ============================================================
# 5. ACTUALIZAR SERVICIOS ECS
# ============================================================
Write-Host "`n=== 5. ACTUALIZANDO SERVICIOS ECS ===" -ForegroundColor Yellow

# Obtener subnets de la VPC default
$VPC_ID = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $Region
$SUBNETS = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[?MapPublicIpOnLaunch].[SubnetId]" --output text --region $Region
$SG_ID = aws ec2 describe-security-groups --group-names psicoconecta-alb-sg --query "SecurityGroups[0].GroupId" --output text --region $Region

Write-Host "  VPC: $VPC_ID" -ForegroundColor Gray
Write-Host "  Subnets: $SUBNETS" -ForegroundColor Gray
Write-Host "  SG: $SG_ID" -ForegroundColor Gray

# Actualizar servicio usuarios
$existingUsers = aws ecs describe-services --cluster $Cluster --services usuarios --region $Region --query "services[?status=='ACTIVE'].serviceName" --output text
if ($existingUsers) {
    Write-Host "  Actualizando servicio usuarios..." -ForegroundColor Yellow
    aws ecs update-service --cluster $Cluster --service usuarios --task-definition $($taskDefArns["usuarios"]) --force-new-deployment --desired-count 1 --region $Region | Out-Null
} else {
    Write-Host "  Creando servicio usuarios..." -ForegroundColor Yellow
    aws ecs create-service --cluster $Cluster --service-name usuarios --task-definition $($taskDefArns["usuarios"]) --desired-count 1 --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" --region $Region | Out-Null
}

# Actualizar servicio puerta-enlace
$existingPE = aws ecs describe-services --cluster $Cluster --services puerta-enlace --region $Region --query "services[?status=='ACTIVE'].serviceName" --output text
if ($existingPE) {
    Write-Host "  Actualizando servicio puerta-enlace..." -ForegroundColor Yellow
    aws ecs update-service --cluster $Cluster --service puerta-enlace --task-definition $($taskDefArns["puerta-enlace"]) --force-new-deployment --desired-count 1 --region $Region | Out-Null
} else {
    Write-Host "  Creando servicio puerta-enlace..." -ForegroundColor Yellow
    aws ecs create-service --cluster $Cluster --service-name puerta-enlace --task-definition $($taskDefArns["puerta-enlace"]) --desired-count 1 --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" --region $Region | Out-Null
}

Write-Host "`n  Servicios actualizados. Esperando que arranquen..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

aws ecs describe-services --cluster $Cluster --services usuarios,puerta-enlace --region $Region --query "services[*].[serviceName,status,runningCount,desiredCount]" --output table

# ============================================================
# 6. OBTENER IP PUBLICA DEL SERVICIO USUARIOS
# ============================================================
Write-Host "`n=== 6. OBTENIENDO IP DEL SERVICIO USUARIOS ===" -ForegroundColor Yellow
Start-Sleep -Seconds 10

$taskArn = aws ecs list-tasks --cluster $Cluster --service-name usuarios --region $Region --query "taskArns[0]" --output text
if ($taskArn -and $taskArn -ne "None") {
    $eniId = aws ecs describe-tasks --cluster $Cluster --tasks $taskArn --region $Region --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text
    if ($eniId -and $eniId -ne "None") {
        $publicIp = aws ec2 describe-network-interfaces --network-interface-ids $eniId --region $Region --query "NetworkInterfaces[0].Association.PublicIp" --output text
        Write-Host "  IP Publica Usuarios: http://${publicIp}:5001" -ForegroundColor Green
        Write-Host "  Health check: http://${publicIp}:5001/health" -ForegroundColor Green
        Write-Host "`n  [!] Guarda esta IP. La necesitas para reconstruir el frontend." -ForegroundColor Cyan
    }
}

# ============================================================
# 7. CONFIGURANDO S3 (SPA ROUTING)
# ============================================================
Write-Host "`n=== 7. CONFIGURANDO S3 ===" -ForegroundColor Yellow

# Configurar error document para SPA routing
$bucketExists = aws s3 ls "s3://$FrontendBucket" 2>$null
if ($LASTEXITCODE -eq 0) {
    aws s3 website "s3://$FrontendBucket" --index-document index.html --error-document index.html
    Write-Host "  S3 website configurado (SPA routing OK)" -ForegroundColor Green

    # Policy publica
    $policy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$FrontendBucket/*"
    }
  ]
}
"@
    $policy | aws s3api put-bucket-policy --bucket $FrontendBucket --policy file:///dev/stdin 2>$null
    # Para Windows:
    $tempPolicy = [System.IO.Path]::GetTempFileName() + ".json"
    $policy | Set-Content -Path $tempPolicy -Encoding UTF8
    aws s3api put-bucket-policy --bucket $FrontendBucket --policy file://$tempPolicy 2>$null
    Remove-Item $tempPolicy -Force
    Write-Host "  Bucket policy actualizada" -ForegroundColor Green
}

# ============================================================
# 8. RECONSTRUIR FRONTEND Y SUBIR
# ============================================================
Write-Host "`n=== 8. RECONSTRUIR FRONTEND CON URL PRODUCCION ===" -ForegroundColor Yellow

# Obtener IP del servicio usuarios
$taskArn = aws ecs list-tasks --cluster $Cluster --service-name usuarios --region $Region --query "taskArns[0]" --output text 2>$null
$apiUrl = "http://localhost:5001"  # fallback
if ($taskArn -and $taskArn -ne "None") {
    $eniId = aws ecs describe-tasks --cluster $Cluster --tasks $taskArn --region $Region --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text
    if ($eniId -and $eniId -ne "None") {
        $publicIp = aws ec2 describe-network-interfaces --network-interface-ids $eniId --region $Region --query "NetworkInterfaces[0].Association.PublicIp" --output text
        if ($publicIp -and $publicIp -ne "None") {
            $apiUrl = "http://${publicIp}:5001"
        }
    }
}

Write-Host "  API URL: $apiUrl" -ForegroundColor Yellow
Set-Location frontend
"VITE_API_URL=$apiUrl" | Set-Content .env
if (-not $GoogleClientId) { $GoogleClientId = Read-Host "Ingresa VITE_GOOGLE_CLIENT_ID (deja vacio para saltar)" }
if ($GoogleClientId) {
    "VITE_GOOGLE_CLIENT_ID=$GoogleClientId" | Add-Content .env
}
npm install 2>$null
npm run build
if ($LASTEXITCODE -eq 0) {
    aws s3 sync dist/ "s3://$FrontendBucket/" --delete
    Write-Host "  Frontend subido a S3" -ForegroundColor Green
} else {
    Write-Host "  [!] Fallo el build del frontend" -ForegroundColor Red
}
Set-Location ..

# ============================================================
# 9. RESUMEN
# ============================================================
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "DESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Frontend: http://$FrontendBucket.s3-website.$Region.amazonaws.com" -ForegroundColor Cyan
Write-Host "Backend (API): $apiUrl/health" -ForegroundColor Cyan
Write-Host "IoT service: corriendo (puerto 5005)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Siguientes pasos manuales:" -ForegroundColor Yellow
Write-Host "  1. Agregar en Google Cloud Console -> Credenciales -> Authorized JS origins:" -ForegroundColor Yellow
Write-Host "     http://$FrontendBucket.s3-website.$Region.amazonaws.com" -ForegroundColor Yellow
Write-Host "  2. Ver logs: aws logs get-log-events --log-group-name /ecs/psicoconecta-usuarios --region $Region" -ForegroundColor Yellow
Write-Host "  3. Seed datos: aws ecs execute-command --cluster $Cluster --task `$(aws ecs list-tasks --cluster $Cluster --service-name usuarios --query 'taskArns[0]' --output text) --container usuarios --interactive --command 'python datos_iniciales.py'" -ForegroundColor Yellow
