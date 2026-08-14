"""
Module CloudWatch — Collector Agent
Collecte les métriques techniques (CPU, réseau) par ressource.
"""

import boto3
from datetime import datetime, timedelta


def fetch_metrics(config: dict) -> list[dict]:
    """
    Appelle CloudWatch et retourne les métriques par ressource/jour.
    Retourne une liste de dicts normalisés.
    """
    cw_config = config["collector"]["cloudwatch"]
    region = config["aws"]["region"]
    lookback = config["collector"]["lookback_days"]
    period = cw_config["period_seconds"]

    client = boto3.client("cloudwatch", region_name=region)

    end = datetime.utcnow()
    start = end - timedelta(days=lookback)

    rows = []

    # EC2 — CPU
    for instance_id in cw_config["ec2_instance_ids"]:
        response = client.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start,
            EndTime=end,
            Period=86400,  # 1 jour
            Statistics=["Average"],
        )
        for point in response["Datapoints"]:
            rows.append({
                "date": point["Timestamp"].strftime("%Y-%m-%d"),
                "service": "AmazonEC2",
                "resource_id": instance_id,
                "cost_usd": None,
                "cpu_avg": round(point["Average"], 4),
                "network_in": None,
                "network_out": None,
                "source": "cloudwatch",
                "account_id": config["aws"]["account_id"],
                "region": region,
            })

    # Lambda — Invocations
    for fn_name in cw_config["lambda_functions"]:
        response = client.get_metric_statistics(
            Namespace="AWS/Lambda",
            MetricName="Invocations",
            Dimensions=[{"Name": "FunctionName", "Value": fn_name}],
            StartTime=start,
            EndTime=end,
            Period=86400,
            Statistics=["Sum"],
        )
        for point in response["Datapoints"]:
            rows.append({
                "date": point["Timestamp"].strftime("%Y-%m-%d"),
                "service": "AWSLambda",
                "resource_id": fn_name,
                "cost_usd": None,
                "cpu_avg": None,
                "network_in": None,
                "network_out": None,
                "source": "cloudwatch",
                "account_id": config["aws"]["account_id"],
                "region": region,
            })

    # RDS — CPU
    rds_id = cw_config["rds_instance_id"]
    response = client.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "DBInstanceIdentifier", "Value": rds_id}],
        StartTime=start,
        EndTime=end,
        Period=86400,
        Statistics=["Average"],
    )
    for point in response["Datapoints"]:
        rows.append({
            "date": point["Timestamp"].strftime("%Y-%m-%d"),
            "service": "AmazonRDS",
            "resource_id": rds_id,
            "cost_usd": None,
            "cpu_avg": round(point["Average"], 4),
            "network_in": None,
            "network_out": None,
            "source": "cloudwatch",
            "account_id": config["aws"]["account_id"],
            "region": region,
        })

    print(f"✅ CloudWatch : {len(rows)} métriques collectées")
    return rows