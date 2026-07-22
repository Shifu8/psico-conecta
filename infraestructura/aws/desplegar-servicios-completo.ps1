# Archivo: desplegar-servicios-completo.ps1
# Descripción: Registra las task definitions y despliega los 6 microservicios en el cluster ECS Fargate.

param(
    [string]$Region = "us-east-2",
    [string]$Cluster = "psicoconecta"
)

$ACCOUNT_ID = $(aws sts get-caller-identity --query Account --output text)
$VPC_ID = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $Region
$SUBNETS_RAW = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[?MapPublicIpOnLaunch].[SubnetId]" --output text --region $Region
$SUBNETS = ($SUBNETS_RAW -split "\s+" | Where-Object { $_ }) -join ","
$SG_ID = aws ec2 describe-security-groups --group-names psicoconecta-alb-sg --query "SecurityGroups[0].GroupId" --output text --region $Region

Write-Host "=== DESPLEGANDO SERVICIOS EN ECS FARGATE ($ACCOUNT_ID) ===" -ForegroundColor Green

# Reemplazar ACCOUNT_ID en todos los JSON de Task Definition
Get-ChildItem infraestructura/aws/task-definition-*.json | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content.Replace("ACCOUNT_ID", $ACCOUNT_ID)
    $content = $content.Replace("060899556466", $ACCOUNT_ID)
    Set-Content $_.FullName $content
}

$SERVICIOS = @(
    @{name="puerta-enlace"; port=5000; taskDef="infraestructura/aws/task-definition-puerta-enlace.json"},
    @{name="usuarios"; port=5001; taskDef="infraestructura/aws/task-definition-usuarios.json"},
    @{name="citas"; port=5002; taskDef="infraestructura/aws/task-definition-citas.json"},
    @{name="teleconsulta"; port=5003; taskDef="infraestructura/aws/task-definition-teleconsulta.json"},
    @{name="pagos"; port=5004; taskDef="infraestructura/aws/task-definition-pagos.json"},
    @{name="iot"; port=5005; taskDef="infraestructura/aws/task-definition-iot.json"}
)

foreach ($svc in $SERVICIOS) {
    Write-Host "`nProcesando $($svc.name)..." -ForegroundColor Yellow

    # Registrar task definition
    $taskDefArn = aws ecs register-task-definition --cli-input-json file://$($svc.taskDef) --region $Region --query "taskDefinition.taskDefinitionArn" --output text
    Write-Host "  - Task Definition registrada: $taskDefArn" -ForegroundColor Green

    # Verificar si el servicio ya existe
    $existing = aws ecs describe-services --cluster $Cluster --services $svc.name --region $Region --query "services[?status=='ACTIVE'].serviceName" --output text

    if ($existing -and $existing -ne "None") {
        aws ecs update-service --cluster $Cluster --service $svc.name --task-definition $taskDefArn --force-new-deployment --region $Region | Out-Null
        Write-Host "  - Servicio ECS $($svc.name) actualizado." -ForegroundColor Green
    } else {
        aws ecs create-service --cluster $Cluster --service-name $svc.name --task-definition $taskDefArn --desired-count 1 --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" --region $Region | Out-Null
        Write-Host "  - Servicio ECS $($svc.name) creado exitosamente." -ForegroundColor Green
    }
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "TODOS LOS SERVICIOS DESPLEGADOS EN ECS" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
