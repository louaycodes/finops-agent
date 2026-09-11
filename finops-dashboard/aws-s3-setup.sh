#!/bin/bash
BUCKET_NAME="finops-dashboard-louay"
REGION="eu-north-1"

# Créer le bucket
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Activer le static website hosting
aws s3 website s3://$BUCKET_NAME \
  --index-document index.html \
  --error-document index.html

# Bucket policy pour accès public
aws s3api put-bucket-policy \
  --bucket $BUCKET_NAME \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::finops-dashboard-louay/*"
    }]
  }'

echo "✅ Bucket configuré : http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"
