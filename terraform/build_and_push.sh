#!/usr/bin/env bash
# Buduje obrazy Docker i pushuje je do ECR.
# Uruchom po `terraform apply` w katalogu infrastructure/.


set -euo pipefail

IMAGE_TAG="${1:-latest}"
AWS_REGION="${AWS_REGION:-eu-north-1}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Pobierz Account ID i URL ECR z outputów Terraforma
cd "$SCRIPT_DIR/infrastructure"
ACCOUNT_ID=$(terraform output -raw aws_account_id)
ECR_BASE="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/cinema"

echo ">>> Logowanie do ECR (region: $AWS_REGION)"
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

SERVICES=(
  film_upload_service
  metadata_service
  transcoding_service
  review_service
  rating_service
)

cd "$PROJECT_ROOT"

for SERVICE in "${SERVICES[@]}"; do
  echo ""
  echo ">>> Budowanie: $SERVICE (tag: $IMAGE_TAG)"
  docker build \
    --platform linux/amd64 \
    -f "${SERVICE}/Dockerfile" \
    -t "${ECR_BASE}/${SERVICE}:${IMAGE_TAG}" \
    .

  echo ">>> Push: ${ECR_BASE}/${SERVICE}:${IMAGE_TAG}"
  docker push "${ECR_BASE}/${SERVICE}:${IMAGE_TAG}"
done

echo ""
echo "✓ Wszystkie obrazy wypchnięte do ECR z tagiem: $IMAGE_TAG"
echo "  Następny krok: cd terraform/services && terraform apply -var='image_tag=$IMAGE_TAG'"
