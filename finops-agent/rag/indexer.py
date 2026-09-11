"""
Module Indexer — RAG Agent
Charge les derniers fichiers JSON depuis S3 (anomalies, forecasts, recommendations),
convertit chaque entrée en texte lisible, génère les embeddings avec sentence-transformers
et indexe dans ChromaDB (collection 'finops', persistée localement).
"""

import json
import os
import boto3
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Chemin de persistance ChromaDB : ../chroma_db/ par rapport à finops-agent/
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")
COLLECTION_NAME = "finops"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def _get_latest_json(client, bucket: str, prefix: str) -> dict | None:
    """
    Retourne le contenu du fichier JSON le plus récent dans bucket/prefix.
    Retourne None si le préfixe est vide.
    """
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objects = response.get("Contents", [])
    if not objects:
        print(f"⚠️  Aucun fichier trouvé dans s3://{bucket}/{prefix} — ignoré")
        return None

    latest = sorted(objects, key=lambda o: o["LastModified"], reverse=True)[0]
    key = latest["Key"]
    obj = client.get_object(Bucket=bucket, Key=key)
    content = obj["Body"].read().decode("utf-8")
    print(f"📥 Chargé : s3://{bucket}/{key}")
    return json.loads(content)


# ─────────────────────────────────────────────────────────────
# Convertisseurs JSON → texte lisible
# ─────────────────────────────────────────────────────────────

def _anomalies_to_chunks(data: dict) -> list[dict]:
    """Convertit le rapport d'anomalies en liste de chunks texte."""
    chunks = []
    generated_at = data.get("generated_at", "N/A")
    summary = data.get("summary", "")

    # Chunk global de résumé
    chunks.append({
        "id": f"anomalies_summary_{generated_at}",
        "text": (
            f"[Rapport d'anomalies — {generated_at}]\n"
            f"Total anomalies : {data.get('total_anomalies', 0)}\n"
            f"Économies estimées : ${data.get('total_estimated_savings_usd', 0):.2f}\n"
            f"Résumé : {summary}"
        ),
        "source": "anomalies",
    })

    for i, anomaly in enumerate(data.get("anomalies", [])):
        chunks.append({
            "id": f"anomaly_{generated_at}_{i}",
            "text": (
                f"[Anomalie {i+1} — {generated_at}]\n"
                f"Service : {anomaly.get('service', 'N/A')}\n"
                f"Ressource : {anomaly.get('resource_id', 'N/A')}\n"
                f"Type : {anomaly.get('type', 'N/A')}\n"
                f"Sévérité : {anomaly.get('severity', 'N/A')}\n"
                f"Description : {anomaly.get('description', '')}\n"
                f"Économies estimées : ${anomaly.get('estimated_savings_usd', 0):.2f}\n"
                f"Recommandation : {anomaly.get('recommendation', '')}"
            ),
            "source": "anomalies",
        })
    return chunks


def _forecast_to_chunks(data: dict) -> list[dict]:
    """Convertit la prévision en chunk texte."""
    generated_at = data.get("generated_at", data.get("period_start", "N/A"))
    text = (
        f"[Prévision budgétaire — {generated_at}]\n"
        f"Période : {data.get('period_start', 'N/A')} → {data.get('period_end', 'N/A')}\n"
        f"Coût total prévu 30 jours : ${data.get('total_predicted_cost_usd', 0)}\n"
        f"Granularité : {data.get('granularity', 'N/A')}\n"
        f"Compte AWS : {data.get('account_id', 'N/A')}"
    )
    return [{"id": f"forecast_{generated_at}", "text": text, "source": "forecast"}]


def _recommendations_to_chunks(data: dict) -> list[dict]:
    """Convertit les recommandations en liste de chunks texte."""
    chunks = []
    generated_at = data.get("generated_at", "N/A")

    chunks.append({
        "id": f"recommendations_summary_{generated_at}",
        "text": (
            f"[Recommandations FinOps — {generated_at}]\n"
            f"Total économies estimées : ${data.get('total_estimated_savings_usd', 0):.2f}\n"
            f"Résumé exécutif : {data.get('executive_summary', '')}"
        ),
        "source": "recommendations",
    })

    for i, rec in enumerate(data.get("recommendations", [])):
        chunks.append({
            "id": f"recommendation_{generated_at}_{i}",
            "text": (
                f"[Recommandation {i+1} — {generated_at}]\n"
                f"Action : {rec.get('action', '')}\n"
                f"Priorité : {rec.get('priority', 'N/A')}\n"
                f"Service : {rec.get('service', 'N/A')}\n"
                f"Économies estimées : ${rec.get('estimated_savings_usd', 0):.2f}\n"
                f"Délai d'implémentation : {rec.get('implementation_delay', 'N/A')}"
            ),
            "source": "recommendations",
        })
    return chunks


# ─────────────────────────────────────────────────────────────
# Point d'entrée
# ─────────────────────────────────────────────────────────────

def index_data(config: dict) -> chromadb.Collection:
    """
    Charge les données S3, génère les embeddings et indexe dans ChromaDB.
    Retourne la collection ChromaDB prête à l'usage.
    """
    bucket = config["storage"]["bucket"]
    region = config["aws"]["region"]

    # ── Chargement S3 ──────────────────────────────────────────
    print("📂 Chargement des données depuis S3...")
    s3 = boto3.client("s3", region_name=region)

    raw_anomalies = _get_latest_json(s3, bucket, "anomalies/")
    raw_forecast = _get_latest_json(s3, bucket, "forecasts/")
    raw_recommendations = _get_latest_json(s3, bucket, "recommendations/")

    # ── Construction des chunks ────────────────────────────────
    chunks = []
    if raw_anomalies:
        chunks += _anomalies_to_chunks(raw_anomalies)
    if raw_forecast:
        chunks += _forecast_to_chunks(raw_forecast)
    if raw_recommendations:
        chunks += _recommendations_to_chunks(raw_recommendations)

    print(f"📝 {len(chunks)} chunks à indexer")

    # ── Embeddings ─────────────────────────────────────────────
    print(f"🔢 Génération des embeddings ({EMBEDDING_MODEL})...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    # ── ChromaDB ───────────────────────────────────────────────
    chroma_path = os.path.abspath(CHROMA_PATH)
    os.makedirs(chroma_path, exist_ok=True)
    print(f"💾 Persistance ChromaDB → {chroma_path}")

    client = chromadb.PersistentClient(path=chroma_path)

    # Supprime la collection si elle existe déjà pour re-indexer proprement
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"source": c["source"]} for c in chunks],
    )

    print(f"✅ ChromaDB indexé : {collection.count()} documents dans '{COLLECTION_NAME}'")
    return collection
