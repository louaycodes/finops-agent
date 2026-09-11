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


def run():
    print("🚀 Forecaster Agent démarré\n")

    config = load_config()

    # Prévision
    forecast = fetch_forecast(config)

    # Sauvegarde
    s3_path = save_forecast(forecast, config)

    print(f"\n✅ Forecaster Agent terminé → {s3_path}")
    print(f"   Coût total prévu 30 jours : ${forecast['total_predicted_cost_usd']}")


if __name__ == "__main__":
    run()