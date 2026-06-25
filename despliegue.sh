#!/bin/bash

# Archivo: despliegue.sh
# Descripción: Script de automatización de tareas y despliegue.
# Módulo: Proyecto General

set -euo pipefail

# ============================================================
# DESPLIEGUE PSICOCONECTA — AWS CLI
# ============================================================
# Requisitos: aws-cli configurado, git, node, python3
# ============================================================

REGION="us-east-1"
NOMBRE="psicoconecta"
BUCKET="${NOMBRE}-frontend-$(date +%s)"

echo "===== 1. BACKEND — Elastic Beanstalk ====="

cd backend/servicios/servicio-usuarios

# Crear zip (sin venv, sin __pycache__, sin .env)
zip -r /tmp/servicio-usuarios.zip . \
  -x "venv/*" "__pycache__/*" ".pytest_cache/*" "*.db" ".env" "instance/*"

# Crear aplicacion EB
aws elasticbeanstalk create-application \
  --application-name "${NOMBRE}-api" \
  --region "$REGION"

# Crear entorno (t2.micro, free tier)
aws elasticbeanstalk create-environment \
  --application-name "${NOMBRE}-api" \
  --environment-name "${NOMBRE}-api-prod" \
  --solution-stack-name "64bit Amazon Linux 2023 v4.3.0 running Python 3.13" \
  --tier Name=WebServer,Type=Standard \
  --option-settings file://<(cat <<EOF
[
  {"Namespace": "aws:autoscaling:launchconfiguration", "OptionName": "InstanceType", "Value": "t2.micro"},
  {"Namespace": "aws:elasticbeanstalk:environment", "OptionName": "EnvironmentType", "Value": "SingleInstance"},
  {"Namespace": "aws:elasticbeanstalk:application:environment", "OptionName": "PORT", "Value": "5001"},
  {"Namespace": "aws:elasticbeanstalk:application:environment", "OptionName": "MODO_DESARROLLO", "Value": "false"},
  {"Namespace": "aws:elasticbeanstalk:application:environment", "OptionName": "GOOGLE_LOGIN_CLIENT_ID", "Value": "339658076678-kah0e205d5asf6ufnlh009lh5i4g8u70.apps.googleusercontent.com"},
  {"Namespace": "aws:elasticbeanstalk:application:environment", "OptionName": "GOOGLE_CLIENT_ID", "Value": "339658076678-8b46grlhh639h3ujsp1fe05bkbqlvnqo.apps.googleusercontent.com"},
  {"Namespace": "aws:elasticbeanstalk:application:environment", "OptionName": "GOOGLE_SENDER_EMAIL", "Value": "brandon.medina@unl.edu.ec"},
  {"Namespace": "aws:elasticbeanstalk:application:environment", "OptionName": "COGNITO_ENABLED", "Value": "false"},
  {"Namespace": "aws:elasticbeanstalk:application:environment", "OptionName": "SECRET_KEY", "Value": "$(openssl rand -hex 32)"},
  {"Namespace": "aws:elasticbeanstalk:application:environment", "OptionName": "JWT_SECRET_KEY", "Value": "$(openssl rand -hex 32)"}
]
EOF
) \
  --region "$REGION"

# Subir version
aws elasticbeanstalk create-application-version \
  --application-name "${NOMBRE}-api" \
  --version-label "v1-$(date +%Y%m%d%H%M%S)" \
  --source-bundle S3Bucket="$(aws elasticbeanstalk describe-environments --application-name "${NOMBRE}-api" --region "$REGION" --query 'Environments[0].CNAME' --output text | cut -d. -f2-)",S3Key=/tmp/servicio-usuarios.zip \
  --region "$REGION"

echo "⏳ Backend desplegandose... (5-10 min)"
echo "  Ver en: https://$REGION.console.aws.amazon.com/elasticbeanstalk/home?region=$REGION#/environment/dashboard?applicationName=${NOMBRE}-api"

cd ../../..

echo ""
echo "===== 2. FRONTEND — S3 + CloudFront ====="

cd frontend

# Build
npm install
npm run build

# Crear bucket S3
aws s3 mb "s3://${BUCKET}" --region "$REGION"
aws s3 website "s3://${BUCKET}" --index-document index.html --error-document index.html

# Policy publica
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${BUCKET}/*"
    }
  ]
}
EOF
aws s3api put-bucket-policy --bucket "${BUCKET}" --policy file:///tmp/bucket-policy.json

# Subir archivos
aws s3 sync dist/ "s3://${BUCKET}/"

echo ""
echo "===== 3. FRONTEND — CloudFront ====="

DIST_ID=$(aws cloudfront create-distribution \
  --origin-domain-name "${BUCKET}.s3-website-${REGION}.amazonaws.com" \
  --default-root-object index.html \
  --query 'Distribution.Id' \
  --output text \
  --region "$REGION")

CF_URL=$(aws cloudfront get-distribution --id "$DIST_ID" --query 'Distribution.DomainName' --output text --region "$REGION")

echo "CloudFront URL: https://${CF_URL}"

echo ""
echo "===== 4. MOSTRAR URLS ====="
echo ""
echo "Frontend: https://${CF_URL}"
echo "Backend:  http://$(aws elasticbeanstalk describe-environments --application-name "${NOMBRE}-api" --region "$REGION" --query 'Environments[0].CNAME' --output text)"
echo "Health:   http://$(aws elasticbeanstalk describe-environments --application-name "${NOMBRE}-api" --region "$REGION" --query 'Environments[0].CNAME' --output text)/health"
echo ""
echo "===== 5. SEED (SSH manual) ====="
echo "aws elasticbeanstalk ssh --environment ${NOMBRE}-api-prod"
echo "cd /var/app/current && python datos_iniciales.py"
echo ""
echo "===== 6. GOOGLE OAUTH ====="
echo "Agregar en https://console.cloud.google.com/apis/credentials"
echo "  Authorized JavaScript origins: https://${CF_URL}"
echo ""
