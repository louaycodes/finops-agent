"""
FinOps RAG API — Point d'entrée Flask
Expose les endpoints /chat, /reindex, /health pour interagir avec le RAG FinOps.

Lancer depuis finops-rag-api/ :
    export GROQ_API_KEY="..."
    ../venv/bin/python app.py
"""

import os
import sys
import yaml
from flask import Flask
from flask_cors import CORS

# ── Ajout de finops-agent/ au sys.path ─────────────────────────────────────────
# Nécessaire pour importer les modules rag/, analyzer/, etc.
FINOPS_AGENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "finops-agent"))
if FINOPS_AGENT_PATH not in sys.path:
    sys.path.insert(0, FINOPS_AGENT_PATH)

# ── Import des modules RAG (après sys.path) ────────────────────────────────────
from rag.indexer import index_data, EMBEDDING_MODEL
from rag.retriever import get_collection
from sentence_transformers import SentenceTransformer

# ── Import des blueprints ──────────────────────────────────────────────────────
from routes.health import health_bp
from routes.index import index_bp
from routes.chat import chat_bp
from routes.api import api_bp


def load_config() -> dict:
    config_path = os.path.join(FINOPS_AGENT_PATH, "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def create_app() -> Flask:
    app = Flask(__name__)

    # ── CORS (pour Angular ou tout autre frontend) ─────────────────────────────
    CORS(app, resources={r"/*": {"origins": "*"}})

    # ── Chargement de la config ────────────────────────────────────────────────
    config = load_config()
    app.finops_config = config

    # ── Chargement du modèle d'embedding (une seule fois au démarrage) ─────────
    print(f"🔢 Chargement du modèle d'embedding ({EMBEDDING_MODEL})...")
    app.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    print("✅ Modèle d'embedding chargé")

    # ── Ouverture de la collection ChromaDB ────────────────────────────────────
    try:
        print("💾 Connexion à ChromaDB...")
        app.collection = get_collection()
        print(f"✅ ChromaDB connecté — {app.collection.count()} documents dans 'finops'")
    except Exception as e:
        print(f"⚠️  ChromaDB vide ou introuvable ({e}) — lancer GET /reindex pour indexer")
        app.collection = None

    # ── Enregistrement des blueprints ─────────────────────────────────────────
    app.register_blueprint(health_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(api_bp)

    return app


if __name__ == "__main__":
    app = create_app()

    print("\n" + "═" * 55)
    print("🚀 FinOps RAG API démarrée")
    print("   POST http://localhost:5001/chat")
    print("   GET  http://localhost:5001/reindex")
    print("   GET  http://localhost:5001/health")
    print("   GET  http://localhost:5001/api/anomalies")
    print("   GET  http://localhost:5001/api/forecast")
    print("   GET  http://localhost:5001/api/recommendations")
    print("   GET  http://localhost:5001/api/metrics")
    print("   POST http://localhost:5001/api/trigger")
    print("═" * 55 + "\n")

    app.run(host="0.0.0.0", port=5001, debug=False)
