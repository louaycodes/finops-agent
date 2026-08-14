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


def run():
    print("🚀 Analyzer Agent démarré\n")

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

    print(f"\n✅ Analyzer Agent terminé → {s3_path}")
    print(f"   Anomalies : {anomalies.get('total_anomalies', 0)}")
    print(f"   Économies estimées : ${anomalies.get('total_estimated_savings_usd', 0):.2f}")
    print(f"   {anomalies.get('summary', '')}")


if __name__ == "__main__":
    run()