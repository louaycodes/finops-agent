"""
Module CloudWatch — Collector Agent
Collecte les métriques techniques dynamiquement selon les ressources découvertes.
"""

import boto3
from datetime import datetime, timedelta

CLOUDWATCH_MAPPING = {
    "ec2:instance": {"namespace": "AWS/EC2", "dimension": "InstanceId", "metrics": ["CPUUtilization", "NetworkIn", "NetworkOut"]},
    "rds:db": {"namespace": "AWS/RDS", "dimension": "DBInstanceIdentifier", "metrics": ["CPUUtilization", "DatabaseConnections"]},
    "lambda:function": {"namespace": "AWS/Lambda", "dimension": "FunctionName", "metrics": ["Invocations", "Duration", "Errors"]},
    "s3:bucket": {"namespace": "AWS/S3", "dimension": "BucketName", "metrics": ["BucketSizeBytes", "NumberOfObjects"]},
    "elasticache:user": {"namespace": "AWS/ElastiCache", "dimension": "CacheClusterId", "metrics": ["CPUUtilization"]},
    "ecs:service": {"namespace": "AWS/ECS", "dimension": "ServiceName", "metrics": ["CPUUtilization", "MemoryUtilization"]},
    "eks:cluster": {"namespace": "AWS/EKS", "dimension": "ClusterName", "metrics": ["node_cpu_utilization"]},
    "dynamodb:table": {"namespace": "AWS/DynamoDB", "dimension": "TableName", "metrics": ["ConsumedReadCapacityUnits", "ConsumedWriteCapacityUnits"]},
}

def fetch_metrics(config: dict) -> list[dict]:
    """
    Appelle CloudWatch dynamiquement pour chaque ressource découverte.
    """
    region = config["aws"]["region"]
    lookback = config["collector"]["lookback_days"]
    # Fallback si period n'est pas défini globalement
    period = config.get("collector", {}).get("cloudwatch", {}).get("period_seconds", 86400)
    
    discovered = config.get("collector", {}).get("discovered_resources", {})

    client = boto3.client("cloudwatch", region_name=region)

    end = datetime.utcnow()
    start = end - timedelta(days=lookback)

    rows = []

    for res_type, res_ids in discovered.items():
        res_type_lower = res_type.lower()
        
        if res_type_lower not in CLOUDWATCH_MAPPING:
            if res_ids:  # logguer uniquement si on a trouvé des ressources
                print(f"⚠️  Ignoré (pas dans mapping) : {res_type} ({len(res_ids)} ressource(s))")
            continue
            
        mapping = CLOUDWATCH_MAPPING[res_type_lower]
        namespace = mapping["namespace"]
        dimension_name = mapping["dimension"]
        metrics = mapping["metrics"]
        
        for res_id in res_ids:
            for metric in metrics:
                try:
                    response = client.get_metric_statistics(
                        Namespace=namespace,
                        MetricName=metric,
                        Dimensions=[{"Name": dimension_name, "Value": res_id}],
                        StartTime=start,
                        EndTime=end,
                        Period=period,
                        Statistics=["Average", "Sum"],
                    )
                    
                    for point in response.get("Datapoints", []):
                        # On prend Average si dispo, sinon Sum
                        val = point.get("Average") if "Average" in point else point.get("Sum", 0.0)
                        
                        # Conversion de la métrique en un nom de colonne standardisé
                        col_name = metric.lower()
                        if metric == "CPUUtilization":
                            col_name = "cpu_avg"
                        elif metric == "NetworkIn":
                            col_name = "network_in"
                        elif metric == "NetworkOut":
                            col_name = "network_out"
                        
                        rows.append({
                            "date": point["Timestamp"].strftime("%Y-%m-%d"),
                            "service": res_type_lower,
                            "resource_id": res_id,
                            "cost_usd": None,
                            "cpu_avg": val if col_name == "cpu_avg" else None,
                            "network_in": val if col_name == "network_in" else None,
                            "network_out": val if col_name == "network_out" else None,
                            col_name: val if col_name not in ["cpu_avg", "network_in", "network_out"] else None,
                            "source": "cloudwatch",
                            "account_id": config["aws"]["account_id"],
                            "region": region,
                        })
                except Exception as e:
                    print(f"⚠️  Erreur métrique {metric} pour {res_id} ({res_type}) : {e}")

    print(f"✅ CloudWatch : {len(rows)} métriques collectées")
    return rows