# Apagado y encendido de recursos AWS

Descripción corta:
Este documento proporciona las instrucciones y comandos necesarios para detener e iniciar de forma segura los recursos aprovisionados en AWS, con el fin de optimizar costos durante periodos de inactividad en entornos de desarrollo o pruebas.

## 1. Alcance de los comandos

Los comandos detallados a continuación afectan exclusivamente a los componentes de computación y base de datos que generan costos por hora (Amazon ECS, Amazon RDS, CloudFront). **No se eliminan datos**, imágenes de Docker, secretos ni registros.

Fecha de ejecución original: 2026-06-24 11:59:53 -05:00
Región usada: `us-east-2`

## 2. Comandos exactos usados para apagar

```powershell
aws cloudwatch disable-alarm-actions --alarm-names psicoconecta-iot-cpu-alta psicoconecta-iot-memoria-alta psicoconecta-puerta-enlace-cpu-alta psicoconecta-puerta-enlace-memoria-alta psicoconecta-usuarios-cpu-alta psicoconecta-usuarios-memoria-alta --region us-east-2

aws ecs update-cluster-settings --cluster psicoconecta --settings name=containerInsights,value=disabled --region us-east-2

aws ecs update-service --cluster psicoconecta --service usuarios --desired-count 0 --region us-east-2
aws ecs update-service --cluster psicoconecta --service puerta-enlace --desired-count 0 --region us-east-2
aws ecs update-service --cluster psicoconecta --service iot --desired-count 0 --region us-east-2
aws ecs wait services-stable --cluster psicoconecta --services usuarios puerta-enlace iot --region us-east-2

aws rds stop-db-instance --db-instance-identifier psicoconecta-postgres --region us-east-2
aws rds describe-db-instances --db-instance-identifier psicoconecta-postgres --region us-east-2 --query "DBInstances[0].DBInstanceStatus" --output text

aws s3api delete-bucket-website --bucket psicoconecta-frontend-060899556466 --region us-east-2
```

Para CloudFront se usa PowerShell porque AWS exige mandar la configuración completa con el `ETag` actual:

```powershell
$distId = "E393PT7BRP38C3"
$cfgRaw = aws cloudfront get-distribution-config --id $distId | ConvertFrom-Json
$etag = $cfgRaw.ETag
$cfgRaw.DistributionConfig.Enabled = $false
$configPath = Join-Path $env:TEMP "psicoconecta-cloudfront-disable.json"
$cfgRaw.DistributionConfig | ConvertTo-Json -Depth 100 | Set-Content -Path $configPath -Encoding ascii
aws cloudfront update-distribution --id $distId --if-match $etag --distribution-config "file://$configPath"
aws cloudfront wait distribution-deployed --id $distId
```

## 3. Comandos para volver a encender

### 3.1 Base de datos
```powershell
aws rds start-db-instance --db-instance-identifier psicoconecta-postgres --region us-east-2
aws rds wait db-instance-available --db-instance-identifier psicoconecta-postgres --region us-east-2
```

### 3.2 Frontend (S3 y CloudFront)
Restaura el website del bucket frontend:
```powershell
aws s3api put-bucket-website --bucket psicoconecta-frontend-060899556466 --region us-east-2 --website-configuration '{"IndexDocument":{"Suffix":"index.html"},"ErrorDocument":{"Key":"index.html"}}'
```

Reactiva CloudFront:
```powershell
$distId = "E393PT7BRP38C3"
$cfgRaw = aws cloudfront get-distribution-config --id $distId | ConvertFrom-Json
$etag = $cfgRaw.ETag
$cfgRaw.DistributionConfig.Enabled = $true
$configPath = Join-Path $env:TEMP "psicoconecta-cloudfront-enable.json"
$cfgRaw.DistributionConfig | ConvertTo-Json -Depth 100 | Set-Content -Path $configPath -Encoding ascii
aws cloudfront update-distribution --id $distId --if-match $etag --distribution-config "file://$configPath"
aws cloudfront wait distribution-deployed --id $distId
```

### 3.3 Backend (ECS)
Vuelve a levantar ECS/Fargate y alarmas:
```powershell
aws ecs update-cluster-settings --cluster psicoconecta --settings name=containerInsights,value=enabled --region us-east-2

aws ecs update-service --cluster psicoconecta --service usuarios --desired-count 1 --region us-east-2
aws ecs update-service --cluster psicoconecta --service puerta-enlace --desired-count 1 --region us-east-2
aws ecs update-service --cluster psicoconecta --service iot --desired-count 1 --region us-east-2
aws ecs wait services-stable --cluster psicoconecta --services usuarios puerta-enlace iot --region us-east-2

aws cloudwatch enable-alarm-actions --alarm-names psicoconecta-iot-cpu-alta psicoconecta-iot-memoria-alta psicoconecta-puerta-enlace-cpu-alta psicoconecta-puerta-enlace-memoria-alta psicoconecta-usuarios-cpu-alta psicoconecta-usuarios-memoria-alta --region us-east-2
```

## 4. Comandos de verificación

```powershell
aws ecs describe-services --cluster psicoconecta --services usuarios puerta-enlace iot --region us-east-2 --query "services[].{serviceName:serviceName,desiredCount:desiredCount,runningCount:runningCount,pendingCount:pendingCount,status:status}" --output table

aws rds describe-db-instances --db-instance-identifier psicoconecta-postgres --region us-east-2 --query "DBInstances[0].{DBInstanceIdentifier:DBInstanceIdentifier,DBInstanceStatus:DBInstanceStatus}" --output table

aws cloudfront get-distribution --id E393PT7BRP38C3 --query "{Id:Distribution.Id,Status:Distribution.Status,Enabled:Distribution.DistributionConfig.Enabled,DomainName:Distribution.DomainName}" --output table

aws cloudwatch describe-alarms --region us-east-2 --query "MetricAlarms[?contains(AlarmName, 'psicoconecta')].{AlarmName:AlarmName,ActionsEnabled:ActionsEnabled}" --output table
```

*(Nota: Una base de datos RDS detenida manualmente puede ser reactivada de forma automática por AWS después de 7 días. Si requiere apagado permanente, debe generarse un snapshot y eliminarse).*
