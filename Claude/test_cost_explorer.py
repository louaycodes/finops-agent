"""
Test de connexion Cost Explorer — Sprint 0
Vérifie que boto3 + credentials + Cost Explorer fonctionnent correctement.
"""

import boto3
from datetime import datetime, timedelta

client = boto3.client("ce", region_name="us-east-1")  # Cost Explorer est toujours en us-east-1

end = datetime.today().strftime("%Y-%m-%d")
start = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")

print(f"📡 Appel Cost Explorer — période : {start} → {end}\n")

response = client.get_cost_and_usage(
    TimePeriod={"Start": start, "End": end},
    Granularity="DAILY",
    Metrics=["UnblendedCost"],
    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
)

total = 0.0
for result in response["ResultsByTime"]:
    date = result["TimePeriod"]["Start"]
    day_total = sum(float(g["Metrics"]["UnblendedCost"]["Amount"]) for g in result["Groups"])
    total += day_total
    print(f"  {date} : ${day_total:.4f}")

print(f"\n✅ Total 7 jours : ${total:.4f}")
print(f"   Compte AWS    : {boto3.client('sts').get_caller_identity()['Account']}")
print(f"   User IAM      : {boto3.client('sts').get_caller_identity()['Arn']}")
