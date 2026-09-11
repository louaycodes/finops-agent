"""
Module Retriever — RAG Agent
Prend une question en texte, génère son embedding, cherche les 5 chunks
les plus proches dans ChromaDB et retourne le contexte assemblé.
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")
COLLECTION_NAME = "finops"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5


def get_collection() -> chromadb.Collection:
    """
    Ouvre la collection ChromaDB persistée (sans ré-indexer).
    """
    chroma_path = os.path.abspath(CHROMA_PATH)
    client = chromadb.PersistentClient(path=chroma_path)
    return client.get_collection(name=COLLECTION_NAME)


def retrieve(question: str, collection: chromadb.Collection, model: SentenceTransformer) -> str:
    """
    Recherche les TOP_K chunks les plus pertinents pour la question.
    Retourne le contexte assemblé sous forme de chaîne de caractères.
    """
    embedding = model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=embedding,
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not docs:
        return "Aucun contexte pertinent trouvé dans la base de connaissances FinOps."

    context_parts = []
    for i, (doc, meta, dist) in enumerate(zip(docs, metadatas, distances)):
        source = meta.get("source", "inconnu")
        similarity = round(1 - dist, 4)  # distance cosine → similarité
        context_parts.append(
            f"--- Contexte {i+1} [source: {source}, similarité: {similarity}] ---\n{doc}"
        )

    return "\n\n".join(context_parts)
