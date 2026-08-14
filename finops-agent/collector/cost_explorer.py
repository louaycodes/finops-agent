"""
Module Cost Explorer — Collector Agent
Collecte les coûts réels AWS par service et par jour.
"""

import boto3
from datetime import datetime, timedelta


def fetch_costs(config: dict) -> list[dict]:
    """
    Appelle Cost Explorer et retourne les coûts par service/jour.
    Retourne une liste de dicts normalisés.
    """
    region = config["aws"]["region"]
    lookback = config["collector"]["lookback_days"]
    services = config["collector"]["services"]

    client = boto3.client("ce", region_name="us-east-1")  # CE est toujours us-east-1

    end = datetime.today().strftime("%Y-%m-%d")
    start = (datetime.today() - timedelta(days=lookback)).strftime("%Y-%m-%d")

    response = client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        Filter={
            "Dimensions": {
                "Key": "SERVICE",
                "Values": services,
            }
        },
    )

    rows = []
    for result in response["ResultsByTime"]:
        date = result["TimePeriod"]["Start"]
        for group in result["Groups"]:
            service = group["Keys"][0]
            cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
            rows.append({
                "date": date,
                "service": service,
                "resource_id": None,
                "cost_usd": cost,
                "cpu_avg": None,
                "network_in": None,
                "network_out": None,
                "source": "cost_explorer",
                "account_id": config["aws"]["account_id"],
                "region": region,
            })

    print(f"✅ Cost Explorer : {len(rows)} lignes collectées ({start} → {end})")
    return rows