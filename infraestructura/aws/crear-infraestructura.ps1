$ACCOUNT_ID = $(aws sts get-caller-identity --query Account --output text)
$REGION = "us-east-2"
$CLUSTER = "psicoconecta"

Write-Host "=== CREANDO INFRAESTRUCTURA PSICOCONECTA EN AWS ===" -ForegroundColor Green

# --- ECR Repositories ---
Write-Host "`n1. Creando repositorios ECR..." -ForegroundColor Yellow
$SERVICIOS = @("puerta-enlace", "usuarios", "citas", "teleconsulta", "pagos", "iot")
foreach ($svc in $SERVICIOS) {
    aws ecr create-repository --repository-name "psicoconecta/$svc" --region $REGION 2>$null
    Write-Host "  - psicoconecta/$svc listo"
}

# --- DynamoDB Tables ---
Write-Host "`n2. Creando tablas DynamoDB..." -ForegroundColor Yellow
$TABLAS = @("emociones", "lecturas_iot", "notificaciones", "logs_iot")
foreach ($t in $TABLAS) {
    aws dynamodb create-table `
        --table-name $t `
        --attribute-definitions AttributeName=id,AttributeType=S `
        --key-schema AttributeName=id,KeyType=HASH `
        --billing-mode PAY_PER_REQUEST `
        --region $REGION 2>$null
    Write-Host "  - $t lista"
}

# --- S3 Bucket ---
Write-Host "`n3. Creando bucket S3 para archivos..." -ForegroundColor Yellow
$BUCKET = "psicoconecta-archivos-$ACCOUNT_ID"
aws s3 mb "s3://$BUCKET" --region $REGION 2>$null
Write-Host "  - $BUCKET listo"

# S3 Bucket for frontend
$FRONTEND_BUCKET = "psicoconecta-frontend-$ACCOUNT_ID"
aws s3 mb "s3://$FRONTEND_BUCKET" --region $REGION 2>$null
aws s3 website "s3://$FRONTEND_BUCKET" --index-document index.html --error-document index.html
Write-Host "  - $FRONTEND_BUCKET listo (static website)"

# --- ECS Cluster ---
Write-Host "`n4. Creando cluster ECS..." -ForegroundColor Yellow
aws ecs create-cluster --cluster-name $CLUSTER --region $REGION 2>$null
Write-Host "  - Cluster $CLUSTER listo"

# --- IAM Role (si no existe) ---
Write-Host "`n5. Verificando IAM role ECS..." -ForegroundColor Yellow
aws iam get-role --role-name ecsTaskExecutionRole 2>$null
if ($LASTEXITCODE -ne 0) {
    aws iam create-role --role-name ecsTaskExecutionRole `
        --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
    aws iam attach-role-policy --role-name ecsTaskExecutionRole `
        --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
    Write-Host "  - Creado ecsTaskExecutionRole"
} else {
    Write-Host "  - ecsTaskExecutionRole ya existe"
}

# --- CloudWatch Logs ---
Write-Host "`n6. Creando grupos de CloudWatch Logs..." -ForegroundColor Yellow
foreach ($svc in $SERVICIOS) {
    aws logs create-log-group --log-group-name "/ecs/psicoconecta-$svc" --region $REGION 2>$null
    Write-Host "  - /ecs/psicoconecta-$svc"
}

# --- ALB ---
Write-Host "`n7. Creando Application Load Balancer..." -ForegroundColor Yellow
$VPC_ID = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $REGION
$SUBNETS = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[?MapPublicIpOnLaunch].[SubnetId]" --output text --region $REGION
$SG_ID = aws ec2 create-security-group --group-name psicoconecta-alb-sg --description "Security group for PsicoConecta ALB" --vpc-id $VPC_ID --region $REGION 2>$null
if ($LASTEXITCODE -eq 0) {
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $REGION
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $REGION
} else {
    $SG_ID = aws ec2 describe-security-groups --group-names psicoconecta-alb-sg --query "SecurityGroups[0].GroupId" --output text --region $REGION
}
Write-Host "  - ALB security group: $SG_ID"
Write-Host "  - VPC: $VPC_ID"
Write-Host "  - Subnets: $SUBNETS"

# --- Secrets Manager ---
Write-Host "`n7. Creando secrets en Secrets Manager..." -ForegroundColor Yellow
$SECRETS = @(
    @{name="psicoconecta/SECRET_KEY"; value="{\"SECRET_KEY\":\"change_this_secret_at_least_32_chars_$( -join ((48..57)+(65..90)+(97..122) | Get-Random -Count 16 | % {[char]$_}))\"}"},
    @{name="psicoconecta/JWT_SECRET_KEY"; value="{\"JWT_SECRET_KEY\":\"change_this_jwt_secret_at_least_32_chars_$( -join ((48..57)+(65..90)+(97..122) | Get-Random -Count 16 | % {[char]$_}))\"}"}
)
foreach ($s in $SECRETS) {
    aws secretsmanager create-secret --name $s.name --secret-string $s.value --region $REGION 2>$null
    Write-Host "  - $($s.name) listo"
}

# --- ALB ---
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "INFRAESTRUCTURA CREADA" -ForegroundColor Green
Write-Host "Account ID: $ACCOUNT_ID" -ForegroundColor Cyan
Write-Host "Region: $REGION" -ForegroundColor Cyan
Write-Host "ECR: psicoconecta/{puerta-enlace,usuarios,citas,teleconsulta,pagos,iot}" -ForegroundColor Cyan
Write-Host "DynamoDB: emociones, lecturas_iot, notificaciones, logs_iot" -ForegroundColor Cyan
Write-Host "S3 Archivos: $BUCKET" -ForegroundColor Cyan
Write-Host "S3 Frontend: $FRONTEND_BUCKET" -ForegroundColor Cyan
Write-Host "Cluster ECS: $CLUSTER" -ForegroundColor Cyan
Write-Host "VPC: $VPC_ID" -ForegroundColor Cyan
Write-Host "Subnets: $SUBNETS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Green
