"""
Module Storage — Recommender Agent
Sauvegarde les recommandations FinOps en JSON dans S3.
"""

import json
import boto3
from datetime import datetime


def save_recommendations(recommendations: dict, config: dict) -> str:
    """
    Sauvegarde le résultat des recommandations en JSON dans S3.
    Retourne le chemin S3 du fichier créé.
    """
    bucket = config["recommender"]["output"]["bucket"]
    prefix = config["recommender"]["output"]["prefix"]
    region = config["aws"]["region"]

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    s3_key = f"{prefix}{timestamp}.json"

    recommendations["generated_at"] = timestamp
    recommendations["account_id"] = config["aws"]["account_id"]

    client = boto3.client("s3", region_name=region)
    client.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=json.dumps(recommendations, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    print(f"✅ Recommandations sauvegardées → s3://{bucket}/{s3_key}")
    return f"s3://{bucket}/{s3_key}"
