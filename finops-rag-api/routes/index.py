"""
Route GET /reindex
Recharge les derniers outputs S3 et re-indexe dans ChromaDB.
"""

from flask import Blueprint, jsonify, current_app
from rag.indexer import index_data

index_bp = Blueprint("index", __name__)


@index_bp.route("/reindex", methods=["GET"])
def reindex():
    try:
        config = current_app.finops_config
        collection = index_data(config)
        doc_count = collection.count()

        # Met à jour la référence partagée dans l'app
        current_app.collection = collection

        return jsonify({
            "status": "success",
            "documents_indexed": doc_count,
        })
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
