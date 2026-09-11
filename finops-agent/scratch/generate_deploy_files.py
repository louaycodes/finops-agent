import os

# Base paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
API_DIR = os.path.join(ROOT_DIR, 'finops-rag-api')
DASHBOARD_DIR = os.path.join(ROOT_DIR, 'finops-dashboard')

# 1. Dockerfile
dockerfile_content = """FROM python:3.12-slim

WORKDIR /app

# Copier les deux dossiers nécessaires
COPY finops-rag-api/ ./finops-rag-api/
COPY finops-agent/ ./finops-agent/

# Installer les dépendances
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r finops-rag-api/requirements.txt

# Variables d'environnement
ENV PYTHONPATH=/app/finops-agent
ENV FLASK_APP=finops-rag-api/app.py

WORKDIR /app/finops-rag-api

EXPOSE 5001

CMD ["python", "app.py"]
"""

with open(os.path.join(API_DIR, 'Dockerfile'), 'w') as f:
    f.write(dockerfile_content)

# 2. docker-compose.yml
docker_compose_content = """version: '3.8'
services:
  finops-api:
    build:
      context: ..
      dockerfile: finops-rag-api/Dockerfile
    ports:
      - "5001:5001"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=eu-north-1
    restart: unless-stopped
"""

with open(os.path.join(API_DIR, 'docker-compose.yml'), 'w') as f:
    f.write(docker_compose_content)

# 3. .env.example
env_example_content = """GROQ_API_KEY=your_groq_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
"""

with open(os.path.join(ROOT_DIR, '.env.example'), 'w') as f:
    f.write(env_example_content)
    
# .env pour les tests Docker locaux
with open(os.path.join(ROOT_DIR, '.env'), 'w') as f:
    f.write(env_example_content)

# 4. deploy.sh
deploy_sh_content = """#!/bin/bash
# Script de déploiement Angular vers S3

BUCKET_NAME="finops-dashboard-louay"
REGION="eu-north-1"

echo "🏗️  Build Angular..."
ng build --configuration production

echo "📦 Upload vers S3..."
aws s3 sync dist/finops-dashboard/browser/ s3://$BUCKET_NAME/ \\
  --region $REGION \\
  --delete \\
  --cache-control "max-age=31536000" \\
  --exclude "index.html"

# index.html sans cache
aws s3 cp dist/finops-dashboard/browser/index.html s3://$BUCKET_NAME/index.html \\
  --region $REGION \\
  --cache-control "no-cache"

echo "✅ Déployé sur http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"
"""

deploy_sh_path = os.path.join(DASHBOARD_DIR, 'deploy.sh')
with open(deploy_sh_path, 'w') as f:
    f.write(deploy_sh_content)
os.chmod(deploy_sh_path, 0o755)

# 5. aws-s3-setup.sh
aws_s3_setup_content = """#!/bin/bash
BUCKET_NAME="finops-dashboard-louay"
REGION="eu-north-1"

# Créer le bucket
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Activer le static website hosting
aws s3 website s3://$BUCKET_NAME \\
  --index-document index.html \\
  --error-document index.html

# Bucket policy pour accès public
aws s3api put-bucket-policy \\
  --bucket $BUCKET_NAME \\
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
"""

s3_setup_path = os.path.join(DASHBOARD_DIR, 'aws-s3-setup.sh')
with open(s3_setup_path, 'w') as f:
    f.write(aws_s3_setup_content)
os.chmod(s3_setup_path, 0o755)

# 6. ec2-setup.sh
ec2_setup_content = """#!/bin/bash
# À exécuter sur l'instance EC2 après connexion SSH

# Installer Docker
sudo apt update
sudo apt install -y docker.io docker-compose git

# Cloner le repo
git clone https://github.com/louaycodes/finops-agent.git
cd finops-agent

# Créer le .env
cat > .env << EOF
GROQ_API_KEY=REMPLACER
SLACK_WEBHOOK_URL=REMPLACER
AWS_ACCESS_KEY_ID=REMPLACER
AWS_SECRET_ACCESS_KEY=REMPLACER
EOF

# Lancer le container
cd finops-rag-api
docker-compose up -d

echo "✅ API Flask lancée sur http://$(curl -s ifconfig.me):5001"
"""

ec2_setup_path = os.path.join(API_DIR, 'ec2-setup.sh')
with open(ec2_setup_path, 'w') as f:
    f.write(ec2_setup_content)
os.chmod(ec2_setup_path, 0o755)

# 7. Update .gitignore
gitignore_path = os.path.join(ROOT_DIR, '.gitignore')
if os.path.exists(gitignore_path):
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()
    if ".env" not in gitignore_content:
        with open(gitignore_path, 'a') as f:
            f.write("\n.env\n")
else:
    with open(gitignore_path, 'w') as f:
        f.write("\n.env\n")

print("Successfully created all deployment files and updated .gitignore.")
