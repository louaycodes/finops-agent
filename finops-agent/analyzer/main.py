"""
Analyzer Agent — Point d'entrée
Orchestre le chargement des données, l'analyse LLM et la sauvegarde.
"""

import yaml
from analyzer.data_loader import load_collected_data, load_synthetic_data, prepare_summary
from analyzer.llm_analyzer import analyze
from analyzer.storage import save_anomalies


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run(config: dict | None = None) -> dict:
    """
    Exécute l'Analyzer Agent.
    Retourne un dict de métriques pour le pipeline LangGraph.
    """
    print("🚀 Analyzer Agent démarré\n")

    if config is None:
        config = load_config()

    # Chargement des données
    df_collected = load_collected_data(config)
    df_synthetic = load_synthetic_data(config)

    # Préparation du résumé
    summary = prepare_summary(df_collected, df_synthetic)
    print(f"\n📊 Résumé préparé : {len(summary)} métriques\n")

    # Analyse LLM
    anomalies = analyze(summary, config)

    # Sauvegarde
    s3_path = save_anomalies(anomalies, config)

    total = anomalies.get('total_anomalies', 0)
    savings = anomalies.get('total_estimated_savings_usd', 0.0)

    print(f"\n✅ Analyzer Agent terminé → {s3_path}")
    print(f"   Anomalies : {total}")
    print(f"   Économies estimées : ${savings:.2f}")
    print(f"   {anomalies.get('summary', '')}")

    return {
        "anomalies_count": total,
        "total_estimated_savings_usd": savings,
        "s3_path": s3_path,
    }


if __name__ == "__main__":
    run()