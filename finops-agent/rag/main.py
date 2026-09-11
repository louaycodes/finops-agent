"""
RAG Agent — Point d'entrée
Orchestre l'indexation des données S3 dans ChromaDB puis lance une boucle
interactive où l'utilisateur peut poser des questions en langage naturel.
"""

import yaml
from sentence_transformers import SentenceTransformer
from rag.indexer import index_data, EMBEDDING_MODEL
from rag.retriever import retrieve
from rag.chat import chat


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def index_only(config: dict | None = None) -> dict:
    """
    Indexe les données S3 dans ChromaDB sans lancer la boucle interactive.
    Utilisé par le pipeline LangGraph.
    Retourne un dict de métriques.
    """
    print("🚀 RAG Indexer démarré\n")

    if config is None:
        config = load_config()

    collection = index_data(config)
    doc_count = collection.count()

    print(f"\n✅ RAG Indexer terminé — {doc_count} documents indexés dans ChromaDB")

    return {
        "indexed_documents": doc_count,
        "collection": "finops",
    }


def run(config: dict | None = None) -> dict:
    """
    Exécute le RAG Agent complet (indexation + boucle interactive).
    Retourne un dict de métriques pour le pipeline LangGraph.
    """
    print("🚀 RAG Agent démarré\n")

    if config is None:
        config = load_config()

    # ── Indexation S3 → ChromaDB ───────────────────────────────
    collection = index_data(config)

    # ── Chargement du modèle d'embedding (partagé) ─────────────
    print(f"\n🔢 Chargement du modèle d'embedding ({EMBEDDING_MODEL})...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # ── Boucle interactive ─────────────────────────────────────
    print("\n" + "═" * 60)
    print("💬 Assistant FinOps AWS — posez vos questions")
    print("   (tapez 'exit' ou 'quit' pour quitter)")
    print("═" * 60 + "\n")

    while True:
        try:
            question = input("❓ Votre question : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Au revoir !")
            break

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            print("👋 Au revoir !")
            break

        # Récupération du contexte
        context = retrieve(question, collection, model)

        # Appel LLM
        print("\n📡 Recherche en cours...")
        answer = chat(question, context, config)

        print(f"\n🤖 Réponse :\n{answer}\n")
        print("─" * 60 + "\n")

    return {
        "indexed_documents": collection.count(),
        "collection": "finops",
    }


if __name__ == "__main__":
    run()
