"""
Module Storage — Collector Agent
Normalise, convertit en Parquet et upload vers S3.
"""

import io
import boto3
import pandas as pd
from datetime import datetime


def save_to_s3(rows: list[dict], config: dict) -> str:
    """
    Prend une liste de dicts normalisés, convertit en Parquet et upload sur S3.
    Retourne le chemin S3 du fichier créé.
    """
    bucket = config["storage"]["bucket"]
    prefix = config["storage"]["prefix"]
    region = config["aws"]["region"]

    df = pd.DataFrame(rows)

    # Typage explicite
    df["date"] = pd.to_datetime(df["date"])
    df["cost_usd"] = pd.to_numeric(df["cost_usd"], errors="coerce")
    df["cpu_avg"] = pd.to_numeric(df["cpu_avg"], errors="coerce")
    df["network_in"] = pd.to_numeric(df["network_in"], errors="coerce")
    df["network_out"] = pd.to_numeric(df["network_out"], errors="coerce")

    # Nom du fichier avec timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    s3_key = f"{prefix}{timestamp}.parquet"

    # Conversion en Parquet en mémoire
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine="pyarrow")
    buffer.seek(0)

    # Upload S3
    client = boto3.client("s3", region_name=region)
    client.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=buffer.getvalue(),
        ContentType="application/octet-stream",
    )

    print(f"✅ Storage : {len(df)} lignes sauvegardées → s3://{bucket}/{s3_key}")
    return f"s3://{bucket}/{s3_key}"