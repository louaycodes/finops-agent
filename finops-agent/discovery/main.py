"""
Main — Discovery Agent
Charge config.yaml, découvre les ressources AWS via Resource Explorer v2,
met à jour la config et l'enregistre.
"""

import yaml
import os
from discovery import resources


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def save_config(config: dict, path: str = "config.yaml"):
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def run(config: dict) -> dict:
    print("\n🚀 Discovery Agent démarré (via Resource Explorer v2)\n")

    region = config.get("aws", {}).get("region", "eu-north-1")
    print(f"🌍 Région ciblée : {region}")

    # ── Découverte ──────────────────────────────────────────────
    discovered = resources.discover_all(region)

    print("\n🔍 Ressources découvertes par type :")
    if not discovered:
        print("   (Aucune ressource découverte ou accès refusé)")
    else:
        for res_type, items in discovered.items():
            print(f"   • {res_type} : {len(items)} ressource(s)")

    # Extraction des services ciblés (gère différentes casses retournées par l'API)
    ec2_ids = discovered.get("ec2:instance", []) or discovered.get("EC2::Instance", [])
    rds_ids = discovered.get("rds:db", []) or discovered.get("RDS::DBInstance", [])
    lambda_fns = discovered.get("lambda:function", []) or discovered.get("Lambda::Function", [])
    s3_buckets = discovered.get("s3:bucket", []) or discovered.get("S3::Bucket", [])

    # ── Mise à jour de la configuration ───────────────────────
    if "collector" not in config:
        config["collector"] = {}
    if "cloudwatch" not in config["collector"]:
        config["collector"]["cloudwatch"] = {}

    cw_config = config["collector"]["cloudwatch"]

    # Mise à jour EC2
    cw_config["ec2_instance_ids"] = ec2_ids

    # Mise à jour RDS (la config CloudWatch utilise rds_instance_id simple)
    if rds_ids:
        cw_config["rds_instance_id"] = rds_ids[0]
    else:
        cw_config["rds_instance_id"] = ""

    # Mise à jour Lambda
    cw_config["lambda_functions"] = lambda_fns
    
    # Ajout des buckets S3
    cw_config["s3_buckets"] = s3_buckets

    # Sauvegarde
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    save_config(config, config_path)

    print(f"\n✅ config.yaml mis à jour avec EC2 ({len(ec2_ids)}), RDS ({len(rds_ids)}), Lambda ({len(lambda_fns)}) et S3 ({len(s3_buckets)}).")

    return {
        "ec2_count": len(ec2_ids),
        "rds_count": len(rds_ids),
        "lambda_count": len(lambda_fns),
        "s3_count": len(s3_buckets)
    }


if __name__ == "__main__":
    config = load_config()
    run(config)
