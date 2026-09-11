"""
Main — Discovery Agent
Charge config.yaml, découvre les ressources AWS via Resource Explorer v2,
met à jour la config avec toutes les ressources dynamiquement, et l'enregistre.
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

    # ── Mise à jour de la configuration ───────────────────────
    if "collector" not in config:
        config["collector"] = {}
        
    # Enregistre le dictionnaire complet retourné par Resource Explorer
    config["collector"]["discovered_resources"] = discovered

    # Sauvegarde
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    save_config(config, config_path)

    total_resources = sum(len(items) for items in discovered.values())
    print(f"\n✅ config.yaml mis à jour avec {total_resources} ressource(s) au total (section discovered_resources).")

    # On retourne un dictionnaire avec le compte par type, plus le total
    metrics = {f"{res_type}_count": len(items) for res_type, items in discovered.items()}
    metrics["total_count"] = total_resources
    
    return metrics


if __name__ == "__main__":
    config = load_config()
    run(config)
