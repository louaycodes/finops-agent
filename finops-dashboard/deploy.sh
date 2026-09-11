#!/bin/bash
# Script de déploiement Angular vers S3

BUCKET_NAME="finops-dashboard-louay"
REGION="eu-north-1"

echo "🏗️  Build Angular..."
ng build --configuration production

echo "📦 Upload vers S3..."
aws s3 sync dist/finops-dashboard/browser/ s3://$BUCKET_NAME/ \
  --region $REGION \
  --delete \
  --cache-control "max-age=31536000" \
  --exclude "index.html"

# index.html sans cache
aws s3 cp dist/finops-dashboard/browser/index.html s3://$BUCKET_NAME/index.html \
  --region $REGION \
  --cache-control "no-cache"

echo "✅ Déployé sur http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"
