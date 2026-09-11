"""
Module Data Loader — Recommender Agent
Charge le dernier fichier JSON des anomalies et des prévisions depuis S3.
"""

import json
import boto3


def _get_latest_json(client, bucket: str, prefix: str) -> dict:
    """
    Retourne le contenu du fichier JSON le plus récent dans bucket/prefix.
    """
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objects = response.get("Contents", [])
    if not objects:
        raise FileNotFoundError(f"Aucun fichier trouvé dans s3://{bucket}/{prefix}")

    # Tri par date de dernière modification (le plus récent en premier)
    latest = sorted(objects, key=lambda o: o["LastModified"], reverse=True)[0]
    key = latest["Key"]

    obj = client.get_object(Bucket=bucket, Key=key)
    content = obj["Body"].read().decode("utf-8")
    print(f"📥 Chargé : s3://{bucket}/{key}")
    return json.loads(content)


def load_inputs(config: dict) -> dict:
    """
    Charge le dernier rapport d'anomalies et la dernière prévision depuis S3.
    Retourne un dict avec les clés 'anomalies' et 'forecast'.
    """
    bucket = config["storage"]["bucket"]
    region = config["aws"]["region"]

    client = boto3.client("s3", region_name=region)

    print("📂 Chargement des données depuis S3...")
    anomalies = _get_latest_json(client, bucket, "anomalies/")
    forecast = _get_latest_json(client, bucket, "forecasts/")

    return {"anomalies": anomalies, "forecast": forecast}
