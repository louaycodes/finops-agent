"""
Script de génération de données CUR synthétiques réalistes
Sprint 0 — FinOps Agent
Génère 90 jours de données de coûts AWS simulées avec anomalies
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

OUTPUT_FILE = "synthetic_cur.csv"
START_DATE = datetime(2026, 1, 1)
DAYS = 90

# Ressources simulées
RESOURCES = {
    "EC2": [
        "i-0a1b2c3d4e5f60001",
        "i-0a1b2c3d4e5f60002",
        "i-0a1b2c3d4e5f60003",
    ],
    "RDS": ["db-finops-db-001"],
    "S3": [
        "finops-cur-data-louay",
        "finops-logs-louay",
        "finops-forgotten-louay",
    ],
    "Lambda": [
        "finops-collector",
        "finops-analyzer",
        "finops-alerter",
    ],
    "CloudWatch": ["cloudwatch-logs-eu-north-1"],
    "AWSDataTransfer": ["datatransfer-eu-north-1"],
}

# Coûts journaliers de base par ressource (en dollars)
BASE_DAILY_COSTS = {
    "i-0a1b2c3d4e5f60001": 0.085,
    "i-0a1b2c3d4e5f60002": 0.085,
    "i-0a1b2c3d4e5f60003": 0.085,
    "db-finops-db-001": 0.48,
    "finops-cur-data-louay": 0.04,
    "finops-logs-louay": 0.03,
    "finops-forgotten-louay": 0.02,
    "finops-collector": 0.005,
    "finops-analyzer": 0.005,
    "finops-alerter": 0.003,
    "cloudwatch-logs-eu-north-1": 0.03,
    "datatransfer-eu-north-1": 0.025,
}

PRODUCT_CODES = {
    "i-0a1b2c3d4e5f60001": "AmazonEC2",
    "i-0a1b2c3d4e5f60002": "AmazonEC2",
    "i-0a1b2c3d4e5f60003": "AmazonEC2",
    "db-finops-db-001": "AmazonRDS",
    "finops-cur-data-louay": "AmazonS3",
    "finops-logs-louay": "AmazonS3",
    "finops-forgotten-louay": "AmazonS3",
    "finops-collector": "AWSLambda",
    "finops-analyzer": "AWSLambda",
    "finops-alerter": "AWSLambda",
    "cloudwatch-logs-eu-north-1": "AmazonCloudWatch",
    "datatransfer-eu-north-1": "AWSDataTransfer",
}

USAGE_TYPES = {
    "i-0a1b2c3d4e5f60001": "EU-BoxUsage:t2.micro",
    "i-0a1b2c3d4e5f60002": "EU-BoxUsage:t2.micro",
    "i-0a1b2c3d4e5f60003": "EU-BoxUsage:t2.micro",
    "db-finops-db-001": "EU-InstanceUsage:db.t3.micro",
    "finops-cur-data-louay": "EU-TimedStorage-ByteHrs",
    "finops-logs-louay": "EU-TimedStorage-ByteHrs",
    "finops-forgotten-louay": "EU-TimedStorage-ByteHrs",
    "finops-collector": "EU-Lambda-GB-Second",
    "finops-analyzer": "EU-Lambda-GB-Second",
    "finops-alerter": "EU-Lambda-GB-Second",
    "cloudwatch-logs-eu-north-1": "EU-DataProcessing-Bytes",
    "datatransfer-eu-north-1": "EU-DataTransfer-Out-Bytes",
}

OPERATIONS = {
    "i-0a1b2c3d4e5f60001": "RunInstances",
    "i-0a1b2c3d4e5f60002": "RunInstances",
    "i-0a1b2c3d4e5f60003": "RunInstances",
    "db-finops-db-001": "CreateDBInstance",
    "finops-cur-data-louay": "PutObject",
    "finops-logs-louay": "PutObject",
    "finops-forgotten-louay": "PutObject",
    "finops-collector": "Invoke",
    "finops-analyzer": "Invoke",
    "finops-alerter": "Invoke",
    "cloudwatch-logs-eu-north-1": "PutLogEvents",
    "datatransfer-eu-north-1": "PublicIP-Out",
}


def is_weekend(date):
    return date.weekday() >= 5


def get_anomaly_multiplier(resource_id, day_index, date):
    """Retourne un multiplicateur de coût selon les anomalies simulées."""

    # Anomalie 1 : EC2 runaway — semaine 5 (jours 28-32)
    if resource_id == "i-0a1b2c3d4e5f60002" and 28 <= day_index <= 32:
        return random.uniform(2.8, 3.5)

    # Anomalie 2 : S3 oublié — croissance progressive à partir du jour 30
    if resource_id == "finops-forgotten-louay" and day_index >= 30:
        growth = 1 + (day_index - 30) * 0.04
        return min(growth, 4.0)

    # Anomalie 3 : Lambda runaway — semaine 7 (jours 42-46)
    if resource_id == "finops-analyzer" and 42 <= day_index <= 46:
        return random.uniform(80, 120)

    # Anomalie 4 : RDS oversized — coût stable mais CPU simulé à 2% (détectable par CloudWatch)
    # Pas de multiplicateur de coût, mais on peut le noter dans les données
    if resource_id == "db-finops-db-001":
        return random.uniform(0.98, 1.02)

    return 1.0


def compute_daily_cost(resource_id, day_index, date):
    base = BASE_DAILY_COSTS[resource_id]

    # Pattern weekend : -30%
    weekend_factor = 0.70 if is_weekend(date) else 1.0

    # Croissance mensuelle : +5% par mois
    monthly_growth = 1 + (day_index // 30) * 0.05

    # Bruit aléatoire : ±5%
    noise = random.uniform(0.95, 1.05)

    # Anomalie
    anomaly = get_anomaly_multiplier(resource_id, day_index, date)

    cost = base * weekend_factor * monthly_growth * noise * anomaly
    return round(cost, 6)


def generate_usage_amount(resource_id, cost):
    """Génère un usage_amount cohérent avec le coût."""
    if "EC2" in PRODUCT_CODES.get(resource_id, ""):
        return round(24.0 + random.uniform(-0.5, 0.5), 4)  # heures
    elif "RDS" in PRODUCT_CODES.get(resource_id, ""):
        return round(24.0 + random.uniform(-0.2, 0.2), 4)
    elif "S3" in PRODUCT_CODES.get(resource_id, ""):
        return round(cost / 0.023 * 1000, 2)  # GB-hours
    elif "Lambda" in PRODUCT_CODES.get(resource_id, ""):
        return round(cost / 0.0000166667, 2)  # GB-seconds
    else:
        return round(cost * 1000, 4)


def main():
    all_resources = [r for resources in RESOURCES.values() for r in resources]

    rows = []
    for day_index in range(DAYS):
        date = START_DATE + timedelta(days=day_index)
        date_start = date.strftime("%Y-%m-%dT00:00:00Z")
        date_end = (date + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")

        for resource_id in all_resources:
            cost = compute_daily_cost(resource_id, day_index, date)
            usage = generate_usage_amount(resource_id, cost)

            rows.append({
                "line_item_usage_start_date": date_start,
                "line_item_usage_end_date": date_end,
                "line_item_product_code": PRODUCT_CODES[resource_id],
                "line_item_usage_type": USAGE_TYPES[resource_id],
                "line_item_operation": OPERATIONS[resource_id],
                "line_item_usage_amount": usage,
                "line_item_unblended_cost": cost,
                "product_region": "eu-north-1",
                "resource_id": resource_id,
                "line_item_line_item_type": "Usage",
            })

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "line_item_usage_start_date",
            "line_item_usage_end_date",
            "line_item_product_code",
            "line_item_usage_type",
            "line_item_operation",
            "line_item_usage_amount",
            "line_item_unblended_cost",
            "product_region",
            "resource_id",
            "line_item_line_item_type",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    total_cost = sum(r["line_item_unblended_cost"] for r in rows)
    print(f"✅ {OUTPUT_FILE} généré — {len(rows)} lignes — Coût total simulé : ${total_cost:.2f}")
    print(f"   Période : {START_DATE.strftime('%Y-%m-%d')} → {(START_DATE + timedelta(days=DAYS-1)).strftime('%Y-%m-%d')}")
    print(f"   Anomalies simulées :")
    print(f"   - EC2 runaway       : jours 28-32 (x3 coût)")
    print(f"   - S3 oublié         : croissance +4%/jour à partir du jour 30")
    print(f"   - Lambda runaway    : jours 42-46 (x100 invocations)")
    print(f"   - RDS oversized     : CPU 2% constant sur 90 jours")


if __name__ == "__main__":
    main()
