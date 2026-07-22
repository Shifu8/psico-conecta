param(
    [string]$Region = "us-east-2",
    [string]$Cluster = "psicoconecta",
    [string]$AlbName = "psicoconecta-alb",
    [string]$AlbSgName = "psicoconecta-alb-sg",
    [string]$CloudFrontId = "E393PT7BRP38C3",
    [switch]$BuildImages
)

$ErrorActionPreference = "Stop"

$accountId = aws sts get-caller-identity --query Account --output text
$databaseSecret = aws secretsmanager describe-secret --secret-id psicoconecta/DATABASE_URL --region $Region --query ARN --output text 2>$null
if ($LASTEXITCODE -ne 0 -or -not $databaseSecret -or $databaseSecret -eq "None") {
    throw "Falta el secreto psicoconecta/DATABASE_URL. Ejecuta infraestructura/aws/configurar-database-url-rds.ps1 con el endpoint RDS existente."
}

$usuarios = @{ name = "usuarios"; container = "usuarios"; port = 5001; dockerfile = "backend/servicios/servicio-usuarios/Dockerfile"; taskDef = "infraestructura/aws/task-definition-usuarios.json"; tg = "psicoconecta-usuarios-tg" }

$servicios = @(
    @{ name = "citas"; container = "citas"; port = 5002; dockerfile = "backend/servicios/servicio-citas/Dockerfile"; taskDef = "infraestructura/aws/task-definition-citas.json"; tg = "psicoconecta-citas-tg"; paths = @("/api/citas*", "/api/disponibilidad*"); priority = 10 },
    @{ name = "teleconsulta"; container = "teleconsulta"; port = 5003; dockerfile = "backend/servicios/servicio-teleconsulta/Dockerfile"; taskDef = "infraestructura/aws/task-definition-teleconsulta.json"; tg = "psicoconecta-teleconsulta-tg"; paths = @("/api/teleconsultas*"); priority = 30 },
    @{ name = "pagos"; container = "pagos"; port = 5004; dockerfile = "backend/servicios/servicio-pagos/Dockerfile"; taskDef = "infraestructura/aws/task-definition-pagos.json"; tg = "psicoconecta-pagos-tg"; paths = @("/api/pagos*"); priority = 40 },
    @{ name = "iot"; container = "iot"; port = 5005; dockerfile = "backend/servicios/servicio-inteligencia-iot/Dockerfile"; taskDef = "infraestructura/aws/task-definition-iot.json"; tg = "psicoconecta-iot-tg"; paths = @("/api/iot*"); priority = 50 }
)

if ($BuildImages) {
    aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$accountId.dkr.ecr.$Region.amazonaws.com"
    foreach ($svc in @($usuarios) + $servicios) {
        $repo = "psicoconecta/$($svc.name)"
        $uri = "$accountId.dkr.ecr.$Region.amazonaws.com/$repo"
        aws ecr create-repository --repository-name $repo --region $Region 2>$null | Out-Null
        docker build -t $repo -f $svc.dockerfile .
        docker tag "$repo`:latest" "$uri`:latest"
        docker push "$uri`:latest"
    }
}

$vpcId = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --region $Region --query "Vpcs[0].VpcId" --output text
$subnets = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpcId" --region $Region --query "Subnets[?MapPublicIpOnLaunch].[SubnetId]" --output text
$subnetList = $subnets -split "\s+" | Where-Object { $_ }
$subnetCsv = $subnetList -join ","
$albSgId = aws ec2 describe-security-groups --filters "Name=group-name,Values=$AlbSgName" "Name=vpc-id,Values=$vpcId" --region $Region --query "SecurityGroups[0].GroupId" --output text
$albArn = aws elbv2 describe-load-balancers --names $AlbName --region $Region --query "LoadBalancers[0].LoadBalancerArn" --output text
$listenerArn = aws elbv2 describe-listeners --load-balancer-arn $albArn --region $Region --query "Listeners[0].ListenerArn" --output text

$oldAction = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$usuariosTargetGroupArn = $null
$usuariosTargetGroupArn = aws elbv2 describe-target-groups --names $usuarios.tg --region $Region --query "TargetGroups[0].TargetGroupArn" --output text 2>$null
$ErrorActionPreference = $oldAction
if ($LASTEXITCODE -ne 0 -or -not $usuariosTargetGroupArn -or $usuariosTargetGroupArn -eq "None") {
    $usuariosTargetGroupArn = aws elbv2 create-target-group --name $usuarios.tg --protocol HTTP --port $usuarios.port --target-type ip --vpc-id $vpcId --health-check-path /health --region $Region --query "TargetGroups[0].TargetGroupArn" --output text
}
aws elbv2 modify-target-group --target-group-arn $usuariosTargetGroupArn --health-check-path /health --health-check-interval-seconds 15 --healthy-threshold-count 2 --unhealthy-threshold-count 2 --matcher HttpCode=200 --region $Region | Out-Null
aws elbv2 modify-listener --listener-arn $listenerArn --default-actions "Type=forward,TargetGroupArn=$usuariosTargetGroupArn" --region $Region | Out-Null

$usuariosTaskDefArn = aws ecs register-task-definition --cli-input-json "file://$($usuarios.taskDef)" --region $Region --query "taskDefinition.taskDefinitionArn" --output text
$usuariosNetwork = "awsvpcConfiguration={subnets=[$subnetCsv],securityGroups=[$albSgId],assignPublicIp=ENABLED}"
$usuariosLb = "targetGroupArn=$usuariosTargetGroupArn,containerName=$($usuarios.container),containerPort=$($usuarios.port)"
$existingUsuarios = aws ecs describe-services --cluster $Cluster --services usuarios --region $Region --query "services[?status=='ACTIVE'].serviceName" --output text
if ($existingUsuarios) {
    aws ecs update-service --cluster $Cluster --service usuarios --task-definition $usuariosTaskDefArn --load-balancers $usuariosLb --network-configuration $usuariosNetwork --health-check-grace-period-seconds 60 --force-new-deployment --region $Region | Out-Null
} else {
    aws ecs create-service --cluster $Cluster --service-name usuarios --task-definition $usuariosTaskDefArn --desired-count 1 --launch-type FARGATE --load-balancers $usuariosLb --network-configuration $usuariosNetwork --health-check-grace-period-seconds 60 --region $Region | Out-Null
}


foreach ($svc in $servicios) {
    Write-Host "Preparando $($svc.name)..." -ForegroundColor Yellow
    $oldAction = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    aws logs create-log-group --log-group-name "/ecs/psicoconecta-$($svc.name)" --region $Region 2>$null | Out-Null
    $ErrorActionPreference = $oldAction


    $oldAction = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    $targetGroupArn = $null
    $targetGroupArn = aws elbv2 describe-target-groups --names $svc.tg --region $Region --query "TargetGroups[0].TargetGroupArn" --output text 2>$null
    $ErrorActionPreference = $oldAction
    if ($LASTEXITCODE -ne 0 -or -not $targetGroupArn -or $targetGroupArn -eq "None") {
        $targetGroupArn = aws elbv2 create-target-group --name $svc.tg --protocol HTTP --port $svc.port --target-type ip --vpc-id $vpcId --health-check-path /health --region $Region --query "TargetGroups[0].TargetGroupArn" --output text
    }
    aws elbv2 modify-target-group --target-group-arn $targetGroupArn --health-check-path /health --health-check-interval-seconds 15 --healthy-threshold-count 2 --unhealthy-threshold-count 2 --matcher HttpCode=200 --region $Region | Out-Null

    $rules = aws elbv2 describe-rules --listener-arn $listenerArn --region $Region | ConvertFrom-Json
    $existingRule = $rules.Rules | Where-Object {
        $patterns = @($_.Conditions | Where-Object { $_.Field -eq "path-pattern" } | ForEach-Object { $_.Values } | ForEach-Object { $_ })
        @($svc.paths | Where-Object { $patterns -contains $_ }).Count -gt 0
    } | Select-Object -First 1

    $conditions = "Field=path-pattern,Values=$($svc.paths -join ',')"
    $actions = "Type=forward,TargetGroupArn=$targetGroupArn"
    if ($existingRule) {
        aws elbv2 modify-rule --rule-arn $existingRule.RuleArn --conditions $conditions --actions $actions --region $Region | Out-Null
    } else {
        aws elbv2 create-rule --listener-arn $listenerArn --priority $svc.priority --conditions $conditions --actions $actions --region $Region | Out-Null
    }

    $taskDefArn = aws ecs register-task-definition --cli-input-json "file://$($svc.taskDef)" --region $Region --query "taskDefinition.taskDefinitionArn" --output text
    $existingService = aws ecs describe-services --cluster $Cluster --services $svc.name --region $Region --query "services[?status=='ACTIVE'].serviceName" --output text
    $lb = "targetGroupArn=$targetGroupArn,containerName=$($svc.container),containerPort=$($svc.port)"
    $network = "awsvpcConfiguration={subnets=[$subnetCsv],securityGroups=[$albSgId],assignPublicIp=ENABLED}"
    if ($existingService) {
        aws ecs update-service --cluster $Cluster --service $svc.name --task-definition $taskDefArn --load-balancers $lb --network-configuration $network --health-check-grace-period-seconds 60 --force-new-deployment --region $Region | Out-Null
    } else {
        aws ecs create-service --cluster $Cluster --service-name $svc.name --task-definition $taskDefArn --desired-count 1 --launch-type FARGATE --load-balancers $lb --network-configuration $network --health-check-grace-period-seconds 60 --region $Region | Out-Null
    }
}

aws ecs wait services-stable --cluster $Cluster --services usuarios citas teleconsulta pagos iot --region $Region

if ($CloudFrontId) {
    aws cloudfront create-invalidation --distribution-id $CloudFrontId --paths "/api/*" | Out-Null
}

Write-Host "Usuarios, modulos clinicos y servicio IoT desplegados: usuarios, citas, teleconsulta, pagos e iot." -ForegroundColor Green
