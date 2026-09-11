"""
Routes /api/* — FinOps RAG API
Expose les données S3 (anomalies, prévisions, recommandations, métriques)
et le déclenchement asynchrone du pipeline LangGraph.
"""

import json
import threading
import boto3
import pandas as pd
from io import BytesIO
from flask import Blueprint, jsonify, current_app

api_bp = Blueprint("api", __name__, url_prefix="/api")

# ── État du pipeline (thread-safe via un simple flag) ────────────────────────
_pipeline_running = False
_pipeline_lock = threading.Lock()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers S3
# ─────────────────────────────────────────────────────────────────────────────

def _s3_client(config: dict):
    region = config["aws"]["region"]
    return boto3.client("s3", region_name=region)


def _get_latest_json(config: dict, prefix: str) -> dict:
    """Charge le dernier fichier JSON dans bucket/prefix."""
    bucket = config["storage"]["bucket"]
    s3 = _s3_client(config)

    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objects = response.get("Contents", [])
    if not objects:
        raise FileNotFoundError(f"Aucun fichier trouvé dans s3://{bucket}/{prefix}")

    latest = sorted(objects, key=lambda o: o["LastModified"], reverse=True)[0]
    key = latest["Key"]
    obj = s3.get_object(Bucket=bucket, Key=key)
    content = obj["Body"].read().decode("utf-8")
    return json.loads(content)


def _get_all_parquet(config: dict, prefix: str) -> pd.DataFrame:
    """Charge et concatène tous les fichiers Parquet dans bucket/prefix."""
    bucket = config["storage"]["bucket"]
    s3 = _s3_client(config)

    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objects = [o for o in response.get("Contents", []) if o["Key"].endswith(".parquet")]
    if not objects:
        raise FileNotFoundError(f"Aucun fichier Parquet dans s3://{bucket}/{prefix}")

    frames = []
    for obj_meta in objects:
        obj = s3.get_object(Bucket=bucket, Key=obj_meta["Key"])
        buf = BytesIO(obj["Body"].read())
        frames.append(pd.read_parquet(buf))

    return pd.concat(frames, ignore_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/anomalies
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/anomalies", methods=["GET"])
def get_anomalies():
    try:
        config = current_app.finops_config
        data = _get_latest_json(config, "anomalies/")
        return jsonify(data)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur S3 : {str(e)}"}), 500


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/forecast
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/forecast", methods=["GET"])
def get_forecast():
    try:
        config = current_app.finops_config
        data = _get_latest_json(config, "forecasts/")
        return jsonify(data)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur S3 : {str(e)}"}), 500


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/recommendations
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/recommendations", methods=["GET"])
def get_recommendations():
    try:
        config = current_app.finops_config
        data = _get_latest_json(config, "recommendations/")
        return jsonify(data)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur S3 : {str(e)}"}), 500


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/metrics
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/metrics", methods=["GET"])
def get_metrics():
    try:
        config = current_app.finops_config
        df = _get_all_parquet(config, config["storage"]["prefix"])

        # ── Détection de la colonne de coût ──────────────────────────────────
        cost_col = next(
            (c for c in df.columns if "cost" in c.lower() or "amount" in c.lower()),
            None,
        )
        service_col = next(
            (c for c in df.columns if "service" in c.lower()),
            None,
        )
        date_col = next(
            (c for c in df.columns if "date" in c.lower() or "time" in c.lower() or "period" in c.lower()),
            None,
        )

        # ── Agrégations ───────────────────────────────────────────────────────
        total_cost = float(df[cost_col].sum()) if cost_col else None

        cost_by_service = {}
        if cost_col and service_col:
            grouped = df.groupby(service_col)[cost_col].sum().sort_values(ascending=False)
            cost_by_service = {k: round(float(v), 4) for k, v in grouped.items()}

        monitored_resources = (
            int(df[service_col].nunique()) if service_col else len(df)
        )

        last_collected = None
        if date_col:
            try:
                last_collected = str(df[date_col].max())
            except Exception:
                last_collected = None

        return jsonify({
            "total_cost_usd": round(total_cost, 4) if total_cost is not None else None,
            "cost_by_service_usd": cost_by_service,
            "monitored_resources": monitored_resources,
            "total_rows": len(df),
            "last_collected": last_collected,
        })

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur agrégation : {str(e)}"}), 500


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/trigger
# ─────────────────────────────────────────────────────────────────────────────

def _run_pipeline(config: dict):
    """Cible du thread : lance le pipeline LangGraph complet."""
    global _pipeline_running
    try:
        from pipeline.main import run as pipeline_run
        print("🏗️  [Pipeline] Démarrage en arrière-plan...")
        pipeline_run()
        print("✅ [Pipeline] Terminé avec succès")
    except Exception as e:
        print(f"❌ [Pipeline] Erreur : {e}")
    finally:
        with _pipeline_lock:
            _pipeline_running = False


@api_bp.route("/trigger", methods=["POST"])
def trigger_pipeline():
    global _pipeline_running

    with _pipeline_lock:
        if _pipeline_running:
            return jsonify({
                "status": "already_running",
                "message": "Le pipeline est déjà en cours d'exécution.",
            }), 409

        config = current_app.finops_config
        _pipeline_running = True
        thread = threading.Thread(
            target=_run_pipeline,
            args=(config,),
            daemon=True,
            name="finops-pipeline",
        )
        thread.start()

    return jsonify({
        "status": "pipeline_started",
        "message": "Pipeline lancé en arrière-plan. Résultats disponibles dans S3.",
    })
