"""
Route POST /chat
Reçoit une question, récupère le contexte ChromaDB, appelle Groq et retourne la réponse.
"""

from flask import Blueprint, request, jsonify, current_app
from rag.retriever import retrieve
from rag.chat import chat as rag_chat

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data or "question" not in data:
        return jsonify({"error": "Body JSON requis avec le champ 'question'"}), 400

    question = data["question"].strip()
    if not question:
        return jsonify({"error": "La question ne peut pas être vide"}), 400

    try:
        collection = current_app.collection
        model = current_app.embedding_model
        config = current_app.finops_config

        # Récupération du contexte depuis ChromaDB
        context = retrieve(question, collection, model)

        # Comptage des sources retournées
        sources_count = context.count("--- Contexte ")

        # Génération de la réponse via Groq
        answer = rag_chat(question, context, config)

        return jsonify({
            "answer": answer,
            "sources_count": sources_count,
        })

    except EnvironmentError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Erreur interne : {str(e)}"}), 500
