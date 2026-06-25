# Archivo: configurar-monitoreo-cloudwatch.ps1
# Descripción: Script de automatización de tareas y despliegue.
# Módulo: Infraestructura

param(
    [string]$Region = "us-east-2",
    [string]$Cluster = "psicoconecta",
    [string[]]$Servicios = @("puerta-enlace", "usuarios", "citas", "teleconsulta", "pagos", "iot"),
    [string]$EmailAlertas = "",
    [string]$LoadBalancerFullName = "",
    [string]$TargetGroupFullName = ""
)

$ErrorActionPreference = "Stop"

Write-Host "=== Configurando monitoreo CloudWatch para PsicoConecta ===" -ForegroundColor Green

$topicArn = aws sns create-topic `
    --name "psicoconecta-alertas" `
    --region $Region `
    --query "TopicArn" `
    --output text

Write-Host "SNS topic: $topicArn" -ForegroundColor Cyan

if ($EmailAlertas) {
    aws sns subscribe `
        --topic-arn $topicArn `
        --protocol email `
        --notification-endpoint $EmailAlertas `
        --region $Region | Out-Null
    Write-Host "Confirma la suscripcion desde el correo: $EmailAlertas" -ForegroundColor Yellow
}

foreach ($svc in $Servicios) {
    $logGroup = "/ecs/psicoconecta-$svc"
    aws logs create-log-group --log-group-name $logGroup --region $Region 2>$null
    aws logs put-retention-policy --log-group-name $logGroup --retention-in-days 30 --region $Region

    $metricName = "Errores$($svc.Replace('-', ''))"
    aws logs put-metric-filter `
        --log-group-name $logGroup `
        --filter-name "errores-$svc" `
        --filter-pattern "?ERROR ?Error ?Exception ?Traceback ?CRITICAL" `
        --metric-transformations "metricName=$metricName,metricNamespace=PsicoConecta/Aplicacion,metricValue=1" `
        --region $Region

    aws cloudwatch put-metric-alarm `
        --alarm-name "psicoconecta-$svc-errores-aplicacion" `
        --alarm-description "Errores detectados en logs de $svc" `
        --namespace "PsicoConecta/Aplicacion" `
        --metric-name $metricName `
        --statistic Sum `
        --period 60 `
        --evaluation-periods 1 `
        --threshold 1 `
        --comparison-operator GreaterThanOrEqualToThreshold `
        --treat-missing-data notBreaching `
        --alarm-actions $topicArn `
        --region $Region

    aws cloudwatch put-metric-alarm `
        --alarm-name "psicoconecta-$svc-cpu-alta" `
        --alarm-description "CPU alta en ECS $svc" `
        --namespace "AWS/ECS" `
        --metric-name CPUUtilization `
        --dimensions "Name=ClusterName,Value=$Cluster" "Name=ServiceName,Value=$svc" `
        --statistic Average `
        --period 60 `
        --evaluation-periods 5 `
        --threshold 75 `
        --comparison-operator GreaterThanThreshold `
        --alarm-actions $topicArn `
        --region $Region

    aws cloudwatch put-metric-alarm `
        --alarm-name "psicoconecta-$svc-memoria-alta" `
        --alarm-description "Memoria alta en ECS $svc" `
        --namespace "AWS/ECS" `
        --metric-name MemoryUtilization `
        --dimensions "Name=ClusterName,Value=$Cluster" "Name=ServiceName,Value=$svc" `
        --statistic Average `
        --period 60 `
        --evaluation-periods 5 `
        --threshold 80 `
        --comparison-operator GreaterThanThreshold `
        --alarm-actions $topicArn `
        --region $Region
}

if ($LoadBalancerFullName) {
    aws cloudwatch put-metric-alarm `
        --alarm-name "psicoconecta-alb-5xx" `
        --alarm-description "Errores 5xx generados por el ALB" `
        --namespace "AWS/ApplicationELB" `
        --metric-name HTTPCode_ELB_5XX_Count `
        --dimensions "Name=LoadBalancer,Value=$LoadBalancerFullName" `
        --statistic Sum `
        --period 60 `
        --evaluation-periods 2 `
        --threshold 5 `
        --comparison-operator GreaterThanOrEqualToThreshold `
        --alarm-actions $topicArn `
        --region $Region
}

if ($TargetGroupFullName -and $LoadBalancerFullName) {
    aws cloudwatch put-metric-alarm `
        --alarm-name "psicoconecta-alb-respuesta-lenta" `
        --alarm-description "Tiempo de respuesta alto en targets del ALB" `
        --namespace "AWS/ApplicationELB" `
        --metric-name TargetResponseTime `
        --dimensions "Name=LoadBalancer,Value=$LoadBalancerFullName" "Name=TargetGroup,Value=$TargetGroupFullName" `
        --statistic Average `
        --period 60 `
        --evaluation-periods 5 `
        --threshold 2 `
        --comparison-operator GreaterThanThreshold `
        --alarm-actions $topicArn `
        --region $Region
}

$widgets = @()
$x = 0
$y = 0
foreach ($svc in $Servicios) {
    $widgets += @{
        type = "metric"
        x = $x
        y = $y
        width = 8
        height = 6
        properties = @{
            title = "ECS $svc"
            region = $Region
            metrics = @(
                @("AWS/ECS", "CPUUtilization", "ClusterName", $Cluster, "ServiceName", $svc),
                @(".", "MemoryUtilization", ".", ".", ".", ".")
            )
            stat = "Average"
            period = 60
        }
    }
    $x += 8
    if ($x -ge 24) {
        $x = 0
        $y += 6
    }
}

$dashboard = @{ widgets = $widgets } | ConvertTo-Json -Depth 10 -Compress
aws cloudwatch put-dashboard `
    --dashboard-name "PsicoConecta-Infraestructura" `
    --dashboard-body $dashboard `
    --region $Region

Write-Host "Monitoreo base creado. Revisa CloudWatch > Dashboards > PsicoConecta-Infraestructura." -ForegroundColor Green
