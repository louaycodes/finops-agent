"""
Pipeline Graph — Construit le graphe LangGraph FinOps.

Flux :
  collector → (si failed → END)
            → analyzer → forecaster → (si anomalies == 0 → skip recommender)
                                    → recommender → rag_indexer → END
"""

from langgraph.graph import StateGraph, END
from pipeline.state import FinOpsState
from pipeline.nodes import (
    node_discovery,
    node_collector,
    node_analyzer,
    node_forecaster,
    node_recommender,
    node_rag_indexer,
)


def _route_after_collector(state: FinOpsState) -> str:
    """
    Edge conditionnel après le Collector.
    Si le collector a échoué, on arrête le pipeline.
    """
    if state["collector_status"] == "failed":
        print("\n⛔ Collector en erreur — arrêt du pipeline.")
        return END
    return "analyzer"


def _route_after_analyzer(state: FinOpsState) -> str:
    """
    Edge conditionnel après l'Analyzer.
    Si aucune anomalie n'est détectée, on saute le Recommender.
    """
    if state["anomalies_count"] == 0:
        print("\nℹ️  Aucune anomalie détectée — Recommender ignoré.")
        return "forecaster"
    return "forecaster"


def build_graph() -> StateGraph:
    """
    Construit et compile le graphe LangGraph FinOps.
    """
    graph = StateGraph(FinOpsState)

    # ── Ajout des nœuds ───────────────────────────────────────
    graph.add_node("discovery", node_discovery)
    graph.add_node("collector", node_collector)
    graph.add_node("analyzer", node_analyzer)
    graph.add_node("forecaster", node_forecaster)
    graph.add_node("recommender", node_recommender)
    graph.add_node("rag_indexer", node_rag_indexer)

    # ── Point d'entrée ────────────────────────────────────────
    graph.set_entry_point("discovery")
    graph.add_edge("discovery", "collector")

    # ── Edge conditionnel : collector → analyzer | END ────────
    graph.add_conditional_edges(
        "collector",
        _route_after_collector,
        {
            "analyzer": "analyzer",
            END: END,
        },
    )

    # ── Edge conditionnel : analyzer → forecaster ─────────────
    # (le recommender est toujours exécuté après forecaster si analyzer OK)
    graph.add_conditional_edges(
        "analyzer",
        _route_after_analyzer,
        {
            "forecaster": "forecaster",
        },
    )

    # ── Edges séquentiels ─────────────────────────────────────
    graph.add_edge("forecaster", "recommender")
    graph.add_edge("recommender", "rag_indexer")
    graph.add_edge("rag_indexer", END)

    return graph.compile()
