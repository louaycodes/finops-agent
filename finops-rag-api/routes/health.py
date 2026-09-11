"""
Route GET /health
Vérifie l'état de l'API : ChromaDB disponible + config chargée.
"""

from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    try:
        collection = current_app.collection
        chroma_docs = collection.count()
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

    config = current_app.finops_config
    groq_model = config.get("rag", {}).get("llm", {}).get("model", "N/A")

    return jsonify({
        "status": "ok",
        "chroma_documents": chroma_docs,
        "groq_model": groq_model,
    })
