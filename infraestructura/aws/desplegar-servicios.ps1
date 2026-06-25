# Archivo: desplegar-servicios.ps1
# Descripción: Script de automatización de tareas y despliegue.
# Módulo: Infraestructura

param(
    [string]$Region = "us-east-2",
    [string]$Cluster = "psicoconecta"
)

$ACCOUNT_ID = $(aws sts get-caller-identity --query Account --output text)
$VPC_ID = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $Region
$SUBNETS = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[?MapPublicIpOnLaunch].[SubnetId]" --output text --region $Region
$SG_ID = aws ec2 describe-security-groups --group-names psicoconecta-alb-sg --query "SecurityGroups[0].GroupId" --output text --region $Region

# Agregar reglas de inbound para puertos de backend en el SG
Write-Host "Configurando Security Group para puertos backend..." -ForegroundColor Yellow
$PUERTOS = @(5000, 5001, 5002, 5003, 5004, 5005)
foreach ($puerto in $PUERTOS) {
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port $puerto --cidr 0.0.0.0/0 --region $Region 2>$null
}
Write-Host "  Puertos $($PUERTOS -join ', ') abiertos en SG $SG_ID" -ForegroundColor Green

$SERVICIOS = @(
    @{name="puerta-enlace"; port=5000; taskDef="infraestructura/aws/task-definition-puerta-enlace.json"},
    @{name="usuarios"; port=5001; taskDef="infraestructura/aws/task-definition-usuarios.json"},
    @{name="iot"; port=5005; taskDef="infraestructura/aws/task-definition-iot.json"}
)

# Reemplazar ACCOUNT_ID en task definitions
Get-ChildItem infraestructura/aws/task-definition-*.json | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content.Replace("ACCOUNT_ID", $ACCOUNT_ID)
    Set-Content $_.FullName $content
}

foreach ($svc in $SERVICIOS) {
    Write-Host "Desplegando $($svc.name)..." -ForegroundColor Yellow

    # Registrar task definition
    $taskDefArn = aws ecs register-task-definition --cli-input-json file://$($svc.taskDef) --region $Region --query "taskDefinition.taskDefinitionArn" --output text

    # Crear o actualizar servicio ECS
    $existing = aws ecs describe-services --cluster $Cluster --services $svc.name --region $Region --query "services[?status=='ACTIVE'].serviceName" --output text

    if ($existing) {
        aws ecs update-service --cluster $Cluster --service $svc.name --task-definition $taskDefArn --force-new-deployment --region $Region
        Write-Host "  - Servicio $($svc.name) actualizado"
    } else {
        aws ecs create-service --cluster $Cluster --service-name $svc.name --task-definition $taskDefArn --desired-count 1 --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" --region $Region
        Write-Host "  - Servicio $($svc.name) creado"
    }
}

Write-Host "`nDespliegue completado!" -ForegroundColor Green
Write-Host "Los servicios estan siendo desplegados en ECS Fargate." -ForegroundColor Cyan
