"""
Module Data Loader — Analyzer Agent
Charge les données Parquet depuis S3 et les données synthétiques CUR.
"""

import io
import boto3
import pandas as pd


def load_collected_data(config: dict) -> pd.DataFrame:
    """
    Charge tous les fichiers Parquet du dossier collected/ dans S3.
    """
    bucket = config["storage"]["bucket"]
    prefix = config["storage"]["prefix"]
    region = config["aws"]["region"]

    client = boto3.client("s3", region_name=region)
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    if "Contents" not in response:
        print("⚠️ Aucun fichier Parquet trouvé dans S3.")
        return pd.DataFrame()

    dfs = []
    for obj in response["Contents"]:
        key = obj["Key"]
        if not key.endswith(".parquet"):
            continue
        body = client.get_object(Bucket=bucket, Key=key)["Body"].read()
        df = pd.read_parquet(io.BytesIO(body))
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    print(f"✅ Data Loader : {len(df)} lignes chargées depuis S3 ({len(dfs)} fichiers)")
    return df


def load_synthetic_data(config: dict) -> pd.DataFrame:
    """
    Charge les données CUR synthétiques depuis S3.
    """
    bucket = config["storage"]["bucket"]
    prefix = config["storage"]["synthetic_prefix"]
    region = config["aws"]["region"]

    client = boto3.client("s3", region_name=region)
    key = f"{prefix}synthetic_cur.csv"

    try:
        body = client.get_object(Bucket=bucket, Key=key)["Body"].read()
        df = pd.read_csv(io.BytesIO(body))
        print(f"✅ Synthetic Data : {len(df)} lignes chargées")
        return df
    except Exception as e:
        print(f"⚠️ Données synthétiques non trouvées : {e}")
        return pd.DataFrame()


def prepare_summary(df_collected: pd.DataFrame, df_synthetic: pd.DataFrame) -> dict:
    """
    Prépare un résumé des métriques à envoyer au LLM.
    """
    summary = {}

    if not df_collected.empty:
        cost_data = df_collected[df_collected["source"] == "cost_explorer"].copy()
        cw_data = df_collected[df_collected["source"] == "cloudwatch"].copy()

        if not cost_data.empty:
            summary["cost_by_service"] = (
                cost_data.groupby("service")["cost_usd"]
                .sum()
                .round(4)
                .to_dict()
            )
            summary["total_cost_usd"] = round(cost_data["cost_usd"].sum(), 4)

        if not cw_data.empty:
            summary["cloudwatch_metrics"] = (
                cw_data.groupby("resource_id")["cpu_avg"]
                .mean()
                .round(4)
                .dropna()
                .to_dict()
            )

    if not df_synthetic.empty:
        summary["synthetic_cost_by_service"] = (
            df_synthetic.groupby("line_item_product_code")["line_item_unblended_cost"]
            .sum()
            .round(4)
            .to_dict()
        )
        summary["synthetic_total_cost_usd"] = round(
            df_synthetic["line_item_unblended_cost"].sum(), 4
        )

    return summary