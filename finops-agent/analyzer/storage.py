"""
Module Storage — Analyzer Agent
Sauvegarde les anomalies détectées en JSON dans S3.
"""

import json
import boto3
from datetime import datetime


def save_anomalies(anomalies: dict, config: dict) -> str:
    """
    Sauvegarde le résultat de l'analyse en JSON dans S3.
    Retourne le chemin S3 du fichier créé.
    """
    bucket = config["analyzer"]["output"]["bucket"]
    prefix = config["analyzer"]["output"]["prefix"]
    region = config["aws"]["region"]

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    s3_key = f"{prefix}{timestamp}.json"

    anomalies["generated_at"] = timestamp
    anomalies["account_id"] = config["aws"]["account_id"]

    client = boto3.client("s3", region_name=region)
    client.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=json.dumps(anomalies, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    print(f"✅ Anomalies sauvegardées → s3://{bucket}/{s3_key}")
    return f"s3://{bucket}/{s3_key}"