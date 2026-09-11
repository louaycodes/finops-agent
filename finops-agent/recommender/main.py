"""
Recommender Agent — Point d'entrée
Orchestre le chargement des données, la génération LLM des recommandations et la sauvegarde.
"""

import yaml
from recommender.data_loader import load_inputs
from recommender.llm_recommender import recommend
from recommender.storage import save_recommendations


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run(config: dict | None = None) -> dict:
    """
    Exécute le Recommender Agent.
    Retourne un dict de métriques pour le pipeline LangGraph.
    """
    print("🚀 Recommender Agent démarré\n")

    if config is None:
        config = load_config()

    # Chargement des données (anomalies + prévisions)
    inputs = load_inputs(config)

    # Génération des recommandations via LLM
    recommendations = recommend(inputs, config)

    # Sauvegarde dans S3
    s3_path = save_recommendations(recommendations, config)

    nb = len(recommendations.get("recommendations", []))
    savings = recommendations.get("total_estimated_savings_usd", 0.0)
    summary = recommendations.get("executive_summary", "")

    print(f"\n✅ Recommender Agent terminé → {s3_path}")
    print(f"   Recommandations : {nb}")
    print(f"   Économies estimées : ${savings:.2f}")
    print(f"   {summary}")

    return {
        "recommendations_count": nb,
        "total_estimated_savings_usd": savings,
        "s3_path": s3_path,
    }


if __name__ == "__main__":
    run()
