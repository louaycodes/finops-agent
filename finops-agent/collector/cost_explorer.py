"""
Module Cost Explorer — Collector Agent
Collecte les coûts réels AWS par service et par jour.
"""

import boto3
from datetime import datetime, timedelta


SERVICE_MAPPING = {
    "ec2:instance": "Amazon EC2",
    "rds:db": "Amazon RDS",
    "lambda:function": "AWS Lambda",
    "s3:bucket": "Amazon S3",
    "dynamodb:table": "Amazon DynamoDB",
    "elasticache:user": "Amazon ElastiCache",
    "ecs:service": "Amazon ECS",
    "eks:cluster": "Amazon EKS",
}


def fetch_costs(config: dict) -> list[dict]:
    """
    Appelle Cost Explorer et retourne les coûts par service/jour.
    Retourne une liste de dicts normalisés.
    """
    region = config["aws"]["region"]
    lookback = config["collector"]["lookback_days"]
    
    # ── Construction dynamique de la liste des services ─────────
    discovered = config.get("collector", {}).get("discovered_resources", {})
    services_to_query = set()
    
    for res_type in discovered:
        # Gère la casse retournée par resource-explorer-2
        res_type_lower = res_type.lower()
        if res_type_lower in SERVICE_MAPPING:
            services_to_query.add(SERVICE_MAPPING[res_type_lower])
            
    if not services_to_query:
        print("ℹ️  Aucune ressource découverte, utilisation des services par défaut.")
        services_to_query = config["collector"]["services"]
    else:
        # Toujours ajouter les taxes/transferts si nécessaires, mais on s'en tient au mapping
        services_to_query = list(services_to_query)

    print(f"🔍 Cost Explorer va requêter les services : {services_to_query}")

    client = boto3.client("ce", region_name="us-east-1")  # CE est toujours us-east-1

    end = datetime.today().strftime("%Y-%m-%d")
    start = (datetime.today() - timedelta(days=lookback)).strftime("%Y-%m-%d")

    rows = []
    
    # Cost Explorer ne supporte pas un appel vide pour Values, donc on sécurise
    if not services_to_query:
        return rows

    response = client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        Filter={
            "Dimensions": {
                "Key": "SERVICE",
                "Values": services_to_query,
            }
        },
    )

    for result in response.get("ResultsByTime", []):
        date = result["TimePeriod"]["Start"]
        for group in result.get("Groups", []):
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