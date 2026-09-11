FROM python:3.12-slim

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
