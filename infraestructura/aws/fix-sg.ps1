param([string]$Region = "us-east-2")

# Obtener SG del ALB (usado por los servicios ECS)
$SG_ID = aws ec2 describe-security-groups --group-names psicoconecta-alb-sg --query "SecurityGroups[0].GroupId" --output text --region $Region
Write-Host "Abriendo puertos backend en SG: $SG_ID" -ForegroundColor Yellow

$PUERTOS = @(5000, 5001, 5002, 5003, 5004, 5005)
foreach ($puerto in $PUERTOS) {
    $result = aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port $puerto --cidr 0.0.0.0/0 --region $Region 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Puerto $puerto abierto" -ForegroundColor Green
    }
}
Write-Host "`nReglas actuales del SG:" -ForegroundColor Cyan
aws ec2 describe-security-groups --group-ids $SG_ID --region $Region --query "SecurityGroups[0].IpPermissions[?IpProtocol=='tcp'].{FromPort:FromPort,ToPort:ToPort,Cidr:IpRanges[0].CidrIp}" --output table
