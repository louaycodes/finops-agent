"""
Pipeline Main — Point d'entrée du pipeline FinOps multi-agents LangGraph.
Lance la séquence complète : Collector → Analyzer → Forecaster → Recommender → RAG Indexer
"""

import yaml
from pipeline.graph import build_graph
from pipeline.state import FinOpsState


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _status_icon(status: str) -> str:
    return {"success": "✅", "failed": "❌", "skipped": "⏭️ "}.get(status, "❓")


def run():
    print("═" * 60)
    print("🏗️  FinOps Agent — Pipeline LangGraph")
    print("═" * 60 + "\n")

    config = load_config()

    # ── État initial ──────────────────────────────────────────
    initial_state: FinOpsState = {
        "config": config,
        "collector_status": "skipped",
        "collector_rows": 0,
        "analyzer_status": "skipped",
        "anomalies_count": 0,
        "forecaster_status": "skipped",
        "forecast_total_usd": 0.0,
        "recommender_status": "skipped",
        "recommendations_count": 0,
        "rag_status": "skipped",
        "errors": [],
    }

    # ── Compilation et exécution du graphe ────────────────────
    print("🔧 Compilation du graphe LangGraph...")
    app = build_graph()
    print("▶️  Lancement du pipeline...\n")

    final_state: FinOpsState = app.invoke(initial_state)

    # ── Résumé final ──────────────────────────────────────────
    print("\n" + "═" * 60)
    print("📊 RÉSUMÉ FINAL DU PIPELINE")
    print("═" * 60)

    icon = _status_icon(final_state["collector_status"])
    print(f"  {icon} Collector      → {final_state['collector_status']:8s}  |  {final_state['collector_rows']} lignes collectées")

    icon = _status_icon(final_state["analyzer_status"])
    print(f"  {icon} Analyzer       → {final_state['analyzer_status']:8s}  |  {final_state['anomalies_count']} anomalies détectées")

    icon = _status_icon(final_state["forecaster_status"])
    print(f"  {icon} Forecaster     → {final_state['forecaster_status']:8s}  |  ${final_state['forecast_total_usd']:.2f} prévus (30j)")

    icon = _status_icon(final_state["recommender_status"])
    print(f"  {icon} Recommender    → {final_state['recommender_status']:8s}  |  {final_state['recommendations_count']} recommandations")

    icon = _status_icon(final_state["rag_status"])
    print(f"  {icon} RAG Indexer    → {final_state['rag_status']:8s}  |  ChromaDB mis à jour")

    if final_state["errors"]:
        print("\n⚠️  Erreurs rencontrées :")
        for err in final_state["errors"]:
            print(f"   • {err}")
    else:
        print("\n🎉 Pipeline terminé sans erreur !")

    print("═" * 60 + "\n")


if __name__ == "__main__":
    run()
