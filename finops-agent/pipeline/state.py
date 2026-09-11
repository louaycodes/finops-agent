"""
FinOpsState — Schéma partagé entre tous les nœuds du pipeline LangGraph.
"""

from typing import TypedDict


class FinOpsState(TypedDict):
    # Configuration globale transmise à chaque agent
    config: dict

    # ── Collector ─────────────────────────────────────────────
    collector_status: str    # "success" | "failed" | "skipped"
    collector_rows: int

    # ── Analyzer ──────────────────────────────────────────────
    analyzer_status: str     # "success" | "failed" | "skipped"
    anomalies_count: int

    # ── Forecaster ────────────────────────────────────────────
    forecaster_status: str   # "success" | "failed" | "skipped"
    forecast_total_usd: float

    # ── Recommender ───────────────────────────────────────────
    recommender_status: str  # "success" | "failed" | "skipped"
    recommendations_count: int

    # ── RAG ───────────────────────────────────────────────────
    rag_status: str          # "success" | "failed" | "skipped"

    # ── Erreurs ───────────────────────────────────────────────
    errors: list[str]
