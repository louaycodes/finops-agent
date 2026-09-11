#!/bin/bash
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
