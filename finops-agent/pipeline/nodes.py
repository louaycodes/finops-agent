"""
Pipeline Nodes — Un nœud LangGraph par agent FinOps.
Chaque nœud appelle run(config) de l'agent, met à jour le state,
et capture les exceptions pour ne pas bloquer le pipeline.
"""

from pipeline.state import FinOpsState


# ─────────────────────────────────────────────────────────────
# Nœud Collector
# ─────────────────────────────────────────────────────────────

def node_collector(state: FinOpsState) -> FinOpsState:
    print("\n" + "═" * 60)
    print("🔄 PIPELINE — Nœud Collector")
    print("═" * 60)
    try:
        from collector.main import run
        metrics = run(config=state["config"])
        return {
            **state,
            "collector_status": "success",
            "collector_rows": metrics.get("rows", 0),
        }
    except Exception as exc:
        msg = f"[Collector] {type(exc).__name__}: {exc}"
        print(f"❌ {msg}")
        return {
            **state,
            "collector_status": "failed",
            "errors": state["errors"] + [msg],
        }


# ─────────────────────────────────────────────────────────────
# Nœud Analyzer
# ─────────────────────────────────────────────────────────────

def node_analyzer(state: FinOpsState) -> FinOpsState:
    print("\n" + "═" * 60)
    print("🔄 PIPELINE — Nœud Analyzer")
    print("═" * 60)
    try:
        from analyzer.main import run
        metrics = run(config=state["config"])
        return {
            **state,
            "analyzer_status": "success",
            "anomalies_count": metrics.get("anomalies_count", 0),
        }
    except Exception as exc:
        msg = f"[Analyzer] {type(exc).__name__}: {exc}"
        print(f"❌ {msg}")
        return {
            **state,
            "analyzer_status": "failed",
            "anomalies_count": 0,
            "errors": state["errors"] + [msg],
        }


# ─────────────────────────────────────────────────────────────
# Nœud Forecaster
# ─────────────────────────────────────────────────────────────

def node_forecaster(state: FinOpsState) -> FinOpsState:
    print("\n" + "═" * 60)
    print("🔄 PIPELINE — Nœud Forecaster")
    print("═" * 60)
    try:
        from forecaster.main import run
        metrics = run(config=state["config"])
        return {
            **state,
            "forecaster_status": "success",
            "forecast_total_usd": metrics.get("total_predicted_cost_usd", 0.0),
        }
    except Exception as exc:
        msg = f"[Forecaster] {type(exc).__name__}: {exc}"
        print(f"❌ {msg}")
        return {
            **state,
            "forecaster_status": "failed",
            "forecast_total_usd": 0.0,
            "errors": state["errors"] + [msg],
        }


# ─────────────────────────────────────────────────────────────
# Nœud Recommender
# ─────────────────────────────────────────────────────────────

def node_recommender(state: FinOpsState) -> FinOpsState:
    print("\n" + "═" * 60)
    print("🔄 PIPELINE — Nœud Recommender")
    print("═" * 60)
    try:
        from recommender.main import run
        metrics = run(config=state["config"])
        return {
            **state,
            "recommender_status": "success",
            "recommendations_count": metrics.get("recommendations_count", 0),
        }
    except Exception as exc:
        msg = f"[Recommender] {type(exc).__name__}: {exc}"
        print(f"❌ {msg}")
        return {
            **state,
            "recommender_status": "failed",
            "recommendations_count": 0,
            "errors": state["errors"] + [msg],
        }


# ─────────────────────────────────────────────────────────────
# Nœud RAG Indexer (sans boucle interactive)
# ─────────────────────────────────────────────────────────────

def node_rag_indexer(state: FinOpsState) -> FinOpsState:
    print("\n" + "═" * 60)
    print("🔄 PIPELINE — Nœud RAG Indexer")
    print("═" * 60)
    try:
        from rag.main import index_only
        metrics = index_only(config=state["config"])
        return {
            **state,
            "rag_status": "success",
        }
    except Exception as exc:
        msg = f"[RAG] {type(exc).__name__}: {exc}"
        print(f"❌ {msg}")
        return {
            **state,
            "rag_status": "failed",
            "errors": state["errors"] + [msg],
        }
