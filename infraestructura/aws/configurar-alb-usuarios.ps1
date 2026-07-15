param(
    [string]$Region = "us-east-2",
    [string]$Cluster = "psicoconecta",
    [string]$Service = "usuarios",
    [string]$TaskDefinition = "psicoconecta-usuarios",
    [string]$ContainerName = "usuarios",
    [int]$ContainerPort = 5001,
    [string]$AlbName = "psicoconecta-alb",
    [string]$TargetGroupName = "psicoconecta-usuarios-tg",
    [string]$AlbSgName = "psicoconecta-alb-sg",
    [string]$TaskSgName = "psicoconecta-usuarios-sg",
    [string]$CloudFrontId = "E393PT7BRP38C3"
)

$ErrorActionPreference = "Stop"

Write-Host "=== CONFIGURANDO ALB, SERVICIO ECS Y CLOUDFRONT ===" -ForegroundColor Green

# 1. Obtener VPC y subredes
Write-Host "Buscando VPC por defecto..." -ForegroundColor Yellow
$vpcId = aws ec2 describe-vpcs --filters Name=isDefault,Values=true --region $Region --query "Vpcs[0].VpcId" --output text
Write-Host "VPC: $vpcId" -ForegroundColor Gray

Write-Host "Buscando subredes publicas..." -ForegroundColor Yellow
$subnets = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpcId" --region $Region --query "Subnets[?MapPublicIpOnLaunch].[SubnetId]" --output text
$subnetsList = $subnets -split "\s+" | Where-Object { $_ }
$subnetsCsv = $subnetsList -join ","

if ($subnetsList.Count -lt 2) {
    throw "Se requieren al menos dos subredes publicas en la VPC $vpcId."
}
Write-Host "Subredes: $subnetsCsv" -ForegroundColor Gray

# 2. Configurar Security Groups
Write-Host "Configurando Security Groups..." -ForegroundColor Yellow
$albSgId = aws ec2 describe-security-groups --filters "Name=group-name,Values=$AlbSgName" "Name=vpc-id,Values=$vpcId" --region $Region --query "SecurityGroups[0].GroupId" --output text 2>$null
if ($LASTEXITCODE -ne 0 -or -not $albSgId -or $albSgId -eq "None") {
    $albSgId = aws ec2 create-security-group --group-name $AlbSgName --description "Public access for PsicoConecta ALB" --vpc-id $vpcId --region $Region --query GroupId --output text
    Write-Host "Creado SG ALB: $albSgId" -ForegroundColor Green
}
$oldAction = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$error.Clear()
aws ec2 authorize-security-group-ingress --group-id $albSgId --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $Region 2>$null
$ErrorActionPreference = $oldAction

$taskSgId = aws ec2 describe-security-groups --filters "Name=group-name,Values=$TaskSgName" "Name=vpc-id,Values=$vpcId" --region $Region --query "SecurityGroups[0].GroupId" --output text 2>$null
if ($LASTEXITCODE -ne 0 -or -not $taskSgId -or $taskSgId -eq "None") {
    $taskSgId = aws ec2 create-security-group --group-name $TaskSgName --description "Access from PsicoConecta ALB to usuarios service" --vpc-id $vpcId --region $Region --query GroupId --output text
    Write-Host "Creado SG Task: $taskSgId" -ForegroundColor Green
}
$oldAction = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$error.Clear()
aws ec2 authorize-security-group-ingress --group-id $taskSgId --protocol tcp --port $ContainerPort --source-group $albSgId --region $Region 2>$null
$ErrorActionPreference = $oldAction

# 3. Crear o reutilizar ALB
Write-Host "Creando/verificando ALB..." -ForegroundColor Yellow
$oldAction = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$albArn = $null
$albArn = aws elbv2 describe-load-balancers --names $AlbName --region $Region --query "LoadBalancers[0].LoadBalancerArn" --output text 2>$null
$ErrorActionPreference = $oldAction

if ($LASTEXITCODE -ne 0 -or -not $albArn -or $albArn -eq "None") {
    $error.Clear()
    $subnetsArgs = $subnetsList | ForEach-Object { $_ }
    $albArn = aws elbv2 create-load-balancer --name $AlbName --type application --scheme internet-facing --subnets $subnetsArgs --security-groups $albSgId --region $Region --query "LoadBalancers[0].LoadBalancerArn" --output text
    Write-Host "Creado ALB: $albArn" -ForegroundColor Green
}
aws elbv2 wait load-balancer-available --load-balancer-arns $albArn --region $Region

# 4. Crear o reutilizar Target Group
Write-Host "Creando/verificando Target Group..." -ForegroundColor Yellow
$oldAction = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$targetGroupArn = $null
$targetGroupArn = aws elbv2 describe-target-groups --names $TargetGroupName --region $Region --query "TargetGroups[0].TargetGroupArn" --output text 2>$null
$ErrorActionPreference = $oldAction

if ($LASTEXITCODE -ne 0 -or -not $targetGroupArn -or $targetGroupArn -eq "None") {
    $error.Clear()
    $targetGroupArn = aws elbv2 create-target-group --name $TargetGroupName --protocol HTTP --port $ContainerPort --target-type ip --vpc-id $vpcId --health-check-path /health --region $Region --query "TargetGroups[0].TargetGroupArn" --output text
    Write-Host "Creado Target Group: $targetGroupArn" -ForegroundColor Green
}

aws elbv2 modify-target-group --target-group-arn $targetGroupArn --health-check-path /health --health-check-interval-seconds 15 --healthy-threshold-count 2 --unhealthy-threshold-count 2 --region $Region | Out-Null

# 5. Configurar Listener
Write-Host "Configurando Listener en puerto 80..." -ForegroundColor Yellow
$oldAction = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$listenerArn = $null
$listenerArn = aws elbv2 describe-listeners --load-balancer-arn $albArn --region $Region --query "Listeners[?Port==\`80\`].ListenerArn | [0]" --output text 2>$null
$ErrorActionPreference = $oldAction

if ($LASTEXITCODE -ne 0 -or -not $listenerArn -or $listenerArn -eq "None") {
    $error.Clear()
    aws elbv2 create-listener --load-balancer-arn $albArn --protocol HTTP --port 80 --default-actions "Type=forward,TargetGroupArn=$targetGroupArn" --region $Region | Out-Null
    Write-Host "Listener creado" -ForegroundColor Green
} else {
    aws elbv2 modify-listener --listener-arn $listenerArn --default-actions "Type=forward,TargetGroupArn=$targetGroupArn" --region $Region | Out-Null
    Write-Host "Listener actualizado" -ForegroundColor Green
}

# 6. Asociar ECS servicio con ALB
Write-Host "Conectando el servicio ECS $Service al balanceador..." -ForegroundColor Yellow
aws ecs update-service --cluster $Cluster --service $Service --task-definition $TaskDefinition --load-balancers "targetGroupArn=$targetGroupArn,containerName=$ContainerName,containerPort=$ContainerPort" --network-configuration "awsvpcConfiguration={subnets=[$subnetsCsv],securityGroups=[$taskSgId],assignPublicIp=ENABLED}" --health-check-grace-period-seconds 60 --force-new-deployment --region $Region | Out-Null

Write-Host "Esperando a que el servicio ECS quede estable..." -ForegroundColor Yellow
aws ecs wait services-stable --cluster $Cluster --services $Service --region $Region

$albDns = aws elbv2 describe-load-balancers --load-balancer-arns $albArn --region $Region --query "LoadBalancers[0].DNSName" --output text
Write-Host "`nALB listo: http://$albDns" -ForegroundColor Green
Write-Host "Health check: http://$albDns/health" -ForegroundColor Green

# 7. Actualizar y habilitar CloudFront
if ($CloudFrontId) {
    Write-Host "`nActualizando y habilitando CloudFront ($CloudFrontId)..." -ForegroundColor Yellow
    
    $cfgRaw = aws cloudfront get-distribution-config --id $CloudFrontId | ConvertFrom-Json
    $etag = $cfgRaw.ETag
    
    # Habilitar distribución
    $cfgRaw.DistributionConfig.Enabled = $true
    
    # Actualizar origen del ALB
    $updated = $false
    $cfgRaw.DistributionConfig.Origins.Items | ForEach-Object {
        if ($_.Id -eq "psicoconecta-api-alb") {
            $_.DomainName = $albDns
            $updated = $true
            Write-Host "  Origen 'psicoconecta-api-alb' actualizado a $albDns" -ForegroundColor Green
        }
    }
    
    if (-not $updated) {
        Write-Host "  [!] Advertencia: Origen 'psicoconecta-api-alb' no encontrado en la configuracion de CloudFront." -ForegroundColor Yellow
    }
    
    $configPath = Join-Path $env:TEMP "psicoconecta-cloudfront-enable.json"
    $cfgRaw.DistributionConfig | ConvertTo-Json -Depth 100 | Set-Content -Path $configPath -Encoding ascii
    aws cloudfront update-distribution --id $CloudFrontId --if-match $etag --distribution-config "file://$configPath" | Out-Null
    Remove-Item $configPath -Force
    
    Write-Host "Esperando a que la distribucion de CloudFront se despliegue..." -ForegroundColor Yellow
    aws cloudfront wait distribution-deployed --id $CloudFrontId
    Write-Host "CloudFront habilitado y desplegado con exito!" -ForegroundColor Green
}
