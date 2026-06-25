#!/usr/bin/env bash

# Archivo: configurar-alb-usuarios.sh
# Descripción: Script de automatización de tareas y despliegue.
# Módulo: Infraestructura

set -euo pipefail

REGION="${REGION:-us-east-2}"
CLUSTER="${CLUSTER:-psicoconecta}"
SERVICE="${SERVICE:-usuarios}"
TASK_DEFINITION="${TASK_DEFINITION:-psicoconecta-usuarios}"
CONTAINER_NAME="${CONTAINER_NAME:-usuarios}"
CONTAINER_PORT="${CONTAINER_PORT:-5001}"
ALB_NAME="${ALB_NAME:-psicoconecta-alb}"
TARGET_GROUP_NAME="${TARGET_GROUP_NAME:-psicoconecta-usuarios-tg}"
ALB_SG_NAME="${ALB_SG_NAME:-psicoconecta-alb-sg}"
TASK_SG_NAME="${TASK_SG_NAME:-psicoconecta-usuarios-sg}"

echo "Buscando VPC y subredes publicas en $REGION..."
VPC_ID="$(aws ec2 describe-vpcs \
  --filters Name=isDefault,Values=true \
  --region "$REGION" \
  --query 'Vpcs[0].VpcId' \
  --output text)"

read -r -a SUBNETS <<<"$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" Name=map-public-ip-on-launch,Values=true \
  --region "$REGION" \
  --query 'Subnets[].SubnetId' \
  --output text)"

if (( ${#SUBNETS[@]} < 2 )); then
  echo "Se requieren al menos dos subredes publicas en la VPC $VPC_ID." >&2
  exit 1
fi

echo "Configurando security groups..."
ALB_SG_ID="$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=$ALB_SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
  --region "$REGION" \
  --query 'SecurityGroups[0].GroupId' \
  --output text)"

if [[ "$ALB_SG_ID" == "None" ]]; then
  ALB_SG_ID="$(aws ec2 create-security-group \
    --group-name "$ALB_SG_NAME" \
    --description "Public access for PsicoConecta ALB" \
    --vpc-id "$VPC_ID" \
    --region "$REGION" \
    --query GroupId \
    --output text)"
fi

aws ec2 authorize-security-group-ingress \
  --group-id "$ALB_SG_ID" \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region "$REGION" 2>/dev/null || true

TASK_SG_ID="$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=$TASK_SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
  --region "$REGION" \
  --query 'SecurityGroups[0].GroupId' \
  --output text)"

if [[ "$TASK_SG_ID" == "None" ]]; then
  TASK_SG_ID="$(aws ec2 create-security-group \
    --group-name "$TASK_SG_NAME" \
    --description "Access from PsicoConecta ALB to usuarios service" \
    --vpc-id "$VPC_ID" \
    --region "$REGION" \
    --query GroupId \
    --output text)"
fi

aws ec2 authorize-security-group-ingress \
  --group-id "$TASK_SG_ID" \
  --protocol tcp \
  --port "$CONTAINER_PORT" \
  --source-group "$ALB_SG_ID" \
  --region "$REGION" 2>/dev/null || true

echo "Creando o reutilizando el Application Load Balancer..."
ALB_ARN="$(aws elbv2 describe-load-balancers \
  --names "$ALB_NAME" \
  --region "$REGION" \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text 2>/dev/null || true)"

if [[ -z "$ALB_ARN" || "$ALB_ARN" == "None" ]]; then
  ALB_ARN="$(aws elbv2 create-load-balancer \
    --name "$ALB_NAME" \
    --type application \
    --scheme internet-facing \
    --ip-address-type ipv4 \
    --subnets "${SUBNETS[@]}" \
    --security-groups "$ALB_SG_ID" \
    --region "$REGION" \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text)"
fi

aws elbv2 wait load-balancer-available \
  --load-balancer-arns "$ALB_ARN" \
  --region "$REGION"

aws elbv2 set-security-groups \
  --load-balancer-arn "$ALB_ARN" \
  --security-groups "$ALB_SG_ID" \
  --region "$REGION" >/dev/null

echo "Creando o reutilizando el target group de usuarios..."
TARGET_GROUP_ARN="$(aws elbv2 describe-target-groups \
  --names "$TARGET_GROUP_NAME" \
  --region "$REGION" \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text 2>/dev/null || true)"

if [[ -z "$TARGET_GROUP_ARN" || "$TARGET_GROUP_ARN" == "None" ]]; then
  TARGET_GROUP_ARN="$(aws elbv2 create-target-group \
    --name "$TARGET_GROUP_NAME" \
    --protocol HTTP \
    --port "$CONTAINER_PORT" \
    --target-type ip \
    --vpc-id "$VPC_ID" \
    --health-check-path /health \
    --matcher HttpCode=200 \
    --region "$REGION" \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)"
fi

aws elbv2 modify-target-group \
  --target-group-arn "$TARGET_GROUP_ARN" \
  --health-check-path /health \
  --health-check-interval-seconds 15 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2 \
  --matcher HttpCode=200 \
  --region "$REGION" >/dev/null

echo "Configurando listener HTTP..."
LISTENER_ARN="$(aws elbv2 describe-listeners \
  --load-balancer-arn "$ALB_ARN" \
  --region "$REGION" \
  --query 'Listeners[?Port==`80`].ListenerArn | [0]' \
  --output text)"

if [[ -z "$LISTENER_ARN" || "$LISTENER_ARN" == "None" ]]; then
  aws elbv2 create-listener \
    --load-balancer-arn "$ALB_ARN" \
    --protocol HTTP \
    --port 80 \
    --default-actions "Type=forward,TargetGroupArn=$TARGET_GROUP_ARN" \
    --region "$REGION" >/dev/null
else
  aws elbv2 modify-listener \
    --listener-arn "$LISTENER_ARN" \
    --default-actions "Type=forward,TargetGroupArn=$TARGET_GROUP_ARN" \
    --region "$REGION" >/dev/null
fi

SUBNETS_CSV="$(IFS=,; echo "${SUBNETS[*]}")"
echo "Conectando el servicio ECS $SERVICE al balanceador..."
aws ecs update-service \
  --cluster "$CLUSTER" \
  --service "$SERVICE" \
  --task-definition "$TASK_DEFINITION" \
  --load-balancers "targetGroupArn=$TARGET_GROUP_ARN,containerName=$CONTAINER_NAME,containerPort=$CONTAINER_PORT" \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS_CSV],securityGroups=[$TASK_SG_ID],assignPublicIp=ENABLED}" \
  --health-check-grace-period-seconds 60 \
  --force-new-deployment \
  --region "$REGION" >/dev/null

echo "Esperando a que ECS quede estable..."
aws ecs wait services-stable \
  --cluster "$CLUSTER" \
  --services "$SERVICE" \
  --region "$REGION"

ALB_DNS="$(aws elbv2 describe-load-balancers \
  --load-balancer-arns "$ALB_ARN" \
  --region "$REGION" \
  --query 'LoadBalancers[0].DNSName' \
  --output text)"

echo
echo "ALB listo: http://$ALB_DNS"
echo "Health check: http://$ALB_DNS/health"
echo "Para produccion, configura CloudFront con un behavior /api/* hacia este ALB."
echo "Luego compila el frontend con: VITE_API_URL=https://d1wkhs3cq8vcom.cloudfront.net"
