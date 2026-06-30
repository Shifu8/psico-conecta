# Apagado AWS PsicoConecta

Fecha de ejecucion: 2026-06-24 11:59:53 -05:00
Region usada: `us-east-2`

## Que se apago

- ECS/Fargate: servicios `usuarios`, `puerta-enlace` e `iot` escalados a `desiredCount=0`.
- RDS: instancia `psicoconecta-postgres` detenida.
- CloudWatch: acciones de alarmas deshabilitadas y Container Insights del cluster ECS desactivado.
- SNS: el topic `psicoconecta-alertas` se conservo, pero no recibe disparos de las alarmas porque `ActionsEnabled=false`.
- CloudFront: distribucion `E393PT7BRP38C3` deshabilitada.
- S3 frontend: configuracion de static website eliminada del bucket `psicoconecta-frontend-060899556466`.

No se borraron datos, imagenes ECR, secretos, logs, buckets, ALB ni target groups.

## Comandos exactos usados para apagar

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

Para CloudFront se uso PowerShell porque AWS exige mandar la configuracion completa con el `ETag` actual:

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

## Comandos para volver a subir

Arranca primero la base de datos:

```powershell
aws rds start-db-instance --db-instance-identifier psicoconecta-postgres --region us-east-2
aws rds wait db-instance-available --db-instance-identifier psicoconecta-postgres --region us-east-2
```

Restaura el website del bucket frontend (en PowerShell, se usa un archivo temporal para evitar errores de codificación/escape del JSON):

```powershell
'{"IndexDocument":{"Suffix":"index.html"},"ErrorDocument":{"Key":"index.html"}}' | Set-Content -Path website.json -Encoding ascii
aws s3api put-bucket-website --bucket psicoconecta-frontend-060899556466 --region us-east-2 --website-configuration file://website.json
Remove-Item website.json
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

Vuelve a levantar ECS/Fargate:

```powershell
aws ecs update-cluster-settings --cluster psicoconecta --settings name=containerInsights,value=enabled --region us-east-2

aws ecs update-service --cluster psicoconecta --service usuarios --desired-count 1 --region us-east-2
aws ecs update-service --cluster psicoconecta --service puerta-enlace --desired-count 1 --region us-east-2
aws ecs update-service --cluster psicoconecta --service iot --desired-count 1 --region us-east-2
aws ecs wait services-stable --cluster psicoconecta --services usuarios puerta-enlace iot --region us-east-2
```

Reactiva las alarmas CloudWatch/SNS:

```powershell
aws cloudwatch enable-alarm-actions --alarm-names psicoconecta-iot-cpu-alta psicoconecta-iot-memoria-alta psicoconecta-puerta-enlace-cpu-alta psicoconecta-puerta-enlace-memoria-alta psicoconecta-usuarios-cpu-alta psicoconecta-usuarios-memoria-alta --region us-east-2
```

## Comandos de verificacion

```powershell
aws ecs describe-services --cluster psicoconecta --services usuarios puerta-enlace iot --region us-east-2 --query "services[].{serviceName:serviceName,desiredCount:desiredCount,runningCount:runningCount,pendingCount:pendingCount,status:status}" --output table

aws rds describe-db-instances --db-instance-identifier psicoconecta-postgres --region us-east-2 --query "DBInstances[0].{DBInstanceIdentifier:DBInstanceIdentifier,DBInstanceStatus:DBInstanceStatus}" --output table

aws cloudfront get-distribution --id E393PT7BRP38C3 --query "{Id:Distribution.Id,Status:Distribution.Status,Enabled:Distribution.DistributionConfig.Enabled,DomainName:Distribution.DomainName}" --output table

aws cloudwatch describe-alarms --region us-east-2 --query "MetricAlarms[?contains(AlarmName, 'psicoconecta')].{AlarmName:AlarmName,ActionsEnabled:ActionsEnabled}" --output table
```

Nota: RDS detenido puede reactivarse automaticamente por AWS despues de varios dias. Si se necesita mantenerlo apagado por mas tiempo, conviene revisar su estado periodicamente.
