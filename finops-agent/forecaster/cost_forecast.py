"""
Module Cost Forecast — Forecaster Agent
Utilise l'API native AWS Cost Explorer get_cost_forecast.
"""

import boto3
from datetime import datetime, timedelta


def fetch_forecast(config: dict) -> dict:
    """
    Appelle get_cost_forecast et retourne les prévisions sur 30 jours.
    """
    region = config["aws"]["region"]
    client = boto3.client("ce", region_name="us-east-1")

    start = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    end = (datetime.today() + timedelta(days=31)).strftime("%Y-%m-%d")

    response = client.get_cost_forecast(
        TimePeriod={"Start": start, "End": end},
        Metric="UNBLENDED_COST",
        Granularity="DAILY",
    )

    forecast_results = []
    for result in response["ForecastResultsByTime"]:
        forecast_results.append({
            "date": result["TimePeriod"]["Start"],
            "predicted_cost_usd": round(float(result["MeanValue"]), 4),
            "predicted_cost_lower_usd": round(float(result.get("PredictionIntervalLowerBound", 0)), 4),
            "predicted_cost_upper_usd": round(float(result.get("PredictionIntervalUpperBound", 0)), 4),
        })

    total_predicted = round(float(response["Total"].get("Amount", response["Total"].get("MeanValue", 0))), 4)
    print(f"✅ Forecast : {len(forecast_results)} jours prévus ({start} → {end})")
    print(f"   Coût total prévu : ${total_predicted}")

    return {
        "period": {"start": start, "end": end},
        "total_predicted_cost_usd": total_predicted,
        "daily_forecast": forecast_results,
        "account_id": config["aws"]["account_id"],
        "region": region,
        "generated_at": datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
    }