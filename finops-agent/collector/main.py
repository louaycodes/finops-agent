"""
Collector Agent — Point d'entrée
Orchestre la collecte Cost Explorer + CloudWatch et sauvegarde en S3.
"""

import yaml
from collector.cost_explorer import fetch_costs
from collector.cloudwatch import fetch_metrics
from collector.storage import save_to_s3


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run(config: dict | None = None) -> dict:
    """
    Exécute le Collector Agent.
    Retourne un dict de métriques pour le pipeline LangGraph.
    """
    print("🚀 Collector Agent démarré\n")

    if config is None:
        config = load_config()

    # Collecte Cost Explorer
    cost_rows = fetch_costs(config)

    # Collecte CloudWatch
    cw_rows = fetch_metrics(config)

    # Fusion des deux sources
    all_rows = cost_rows + cw_rows
    print(f"\n📦 Total : {len(all_rows)} lignes à sauvegarder")

    # Sauvegarde S3
    s3_path = save_to_s3(all_rows, config)

    print(f"\n✅ Collector Agent terminé → {s3_path}")

    return {
        "rows": len(all_rows),
        "s3_path": s3_path,
    }


if __name__ == "__main__":
    run()