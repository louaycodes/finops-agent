# État du Projet — Où en est-on exactement

> Ce fichier est mis à jour automatiquement par Claude à la fin de chaque session de travail significative. Au début de toute nouvelle conversation sur le stage, Claude doit lire ce fichier en premier pour savoir exactement où on s'est arrêté, sans que Louay ait à tout réexpliquer.

---

## 📍 Statut actuel

| Champ | Valeur |
|---|---|
| **Sprint en cours** | Sprint 2 |
| **Dernière tâche terminée** | Analyzer Agent — détection d'anomalies via Groq LLM (openai/gpt-oss-120b) |
| **Prochaine tâche prévue** | Sprint 2 — Forecaster Agent (Prophet) |
| **Dernière mise à jour** | 2026-08-14 |
| **Bloqué sur quelque chose ?** | Non |

---

## 🧭 Résumé de la dernière session

*(vide — sera rempli après la première session de travail réelle)*

---

## ⚠️ Points en attente / décisions non tranchées

- ADR-05 (`02_GLOSSAIRE_ET_ADR.md`) — mode de communication Spring Boot ↔ pipeline Python, à trancher au Sprint 3

---

## 📜 Historique des sessions

> Claude ajoute une nouvelle entrée ici à la fin de chaque session de travail, sans écraser les précédentes. Format ci-dessous.

### Format d'une entrée d'historique

```
### [DATE] — Sprint X
**Travaillé sur** : ...
**Terminé** : ...
**En cours / non fini** : ...
**Prochaine étape** : ...
```

### Entrées

### [2026-06-18 → 2026-08-14] — Sprint 0 + Sprint 1
**Travailé sur** : Setup complet AWS + environnement dev + Collector Agent + Analyzer Agent

**Sprint 0 terminé :**
- Compte AWS créé (région eu-north-1), budget 20$ configuré
- IAM user `finops-agent-dev` dans groupe `GroupeDutilisateurStage4emeFinOpsAgent` avec policy custom (ec2, rds, s3, lambda, ce, cloudwatch, events)
- Infra sandbox : 3 EC2 t2.micro, 1 RDS db.t3.micro MySQL (`finops-db`), 3 buckets S3 (`finops-cur-data-louay`, `finops-logs-louay`, `finops-forgotten-louay`), 3 Lambda (`finops-collector`, `finops-analyzer`, `finops-alerter`)
- Cost Explorer activé (IAM billing access activé depuis root)
- Python 3.12 + venv + boto3 + langchain + langgraph installés (fix libexpat via install_name_tool + codesign)
- AWS CLI configuré avec access key de `finops-agent-dev`
- Données synthétiques générées (1080 lignes, 90 jours, 4 anomalies) uploadées dans S3
- Test Cost Explorer validé (`Claude/test_cost_explorer.py`)
- Architecture v1 rédigée (`Claude/ARCHITECTURE_V1.md`)
- Repo Git initialisé et pushé sur https://github.com/louaycodes/finops-agent

**Sprint 1 terminé :**
- Collector Agent : `collector/cost_explorer.py` + `collector/cloudwatch.py` + `collector/storage.py` + `collector/main.py`
- Stockage Parquet dans S3 (`finops-cur-data-louay/collected/`)
- Table Athena `finops.collected` créée et validée
- Lambda `finops-collector` déployée avec layer `AWSSDKPandas-Python314:11`
- EventBridge rule `finops-collector-daily` (rate 1 day) connectée à la Lambda
- Analyzer Agent : `analyzer/data_loader.py` + `analyzer/llm_analyzer.py` + `analyzer/storage.py` + `analyzer/main.py`
- LLM utilisé : Groq API avec modèle `openai/gpt-oss-120b` (pas de ML classique)
- 5 anomalies détectées, scoring High/Medium/Low, 39.75$ d'économies estimées
- Résultat JSON sauvé dans S3 (`finops-cur-data-louay/anomalies/`)
- Config pluggable via `config.yaml` (provider, model, bucket, région configurables)
- Clé Groq retirée du repo + régénérée après détection GitHub Secret Scanning

**Paramètres clés Sprint 1 :**
- Groq model : `openai/gpt-oss-120b`
- Groq API key : dans variable d'environnement `GROQ_API_KEY` (plus dans config.yaml)
- Anomalies output : `s3://finops-cur-data-louay/anomalies/`
- Collected data : `s3://finops-cur-data-louay/collected/`

**Prochaine étape** : Sprint 2 — Forecaster Agent (Prophet) + Recommender Agent (Bedrock) + RAG + LangGraph
