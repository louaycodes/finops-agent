"""
Forecaster Agent — Point d'entrée
Prédit les coûts AWS des 30 prochains jours via get_cost_forecast.
"""

import yaml
from forecaster.cost_forecast import fetch_forecast
from forecaster.storage import save_forecast


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run(config: dict | None = None) -> dict:
    """
    Exécute le Forecaster Agent.
    Retourne un dict de métriques pour le pipeline LangGraph.
    """
    print("🚀 Forecaster Agent démarré\n")

    if config is None:
        config = load_config()

    # Prévision
    forecast = fetch_forecast(config)

    # Sauvegarde
    s3_path = save_forecast(forecast, config)

    total_cost = forecast['total_predicted_cost_usd']
    print(f"\n✅ Forecaster Agent terminé → {s3_path}")
    print(f"   Coût total prévu 30 jours : ${total_cost}")

    return {
        "total_predicted_cost_usd": float(total_cost),
        "s3_path": s3_path,
    }


if __name__ == "__main__":
    run()