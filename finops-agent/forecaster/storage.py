"""
Module Storage — Forecaster Agent
Sauvegarde les prévisions en JSON dans S3.
"""

import json
import boto3
from datetime import datetime


def save_forecast(forecast: dict, config: dict) -> str:
    """
    Sauvegarde le résultat de la prévision en JSON dans S3.
    Retourne le chemin S3 du fichier créé.
    """
    bucket = config["storage"]["bucket"]
    region = config["aws"]["region"]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    s3_key = f"forecasts/{timestamp}.json"

    client = boto3.client("s3", region_name=region)
    client.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=json.dumps(forecast, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    print(f"✅ Forecast sauvegardé → s3://{bucket}/{s3_key}")
    return f"s3://{bucket}/{s3_key}"