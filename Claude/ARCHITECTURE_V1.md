# FinOps Agent — Document d'Architecture v1

**Stagiaire** : Louay Zorai  
**École** : ESPRIT School of Engineering — ArcTIC, 4ème année  
**Entreprise** : Altran Telnet Corporation  
**Date** : Juin 2026

---

## 1. Vue d'ensemble

Un pipeline de 4 agents IA orchestrés par LangGraph qui collecte les coûts AWS, détecte les anomalies de dépenses, prédit les coûts futurs, et génère des recommandations en langage naturel via Amazon Bedrock. Le tout est accessible via une API Spring Boot, un dashboard Angular, et un chatbot RAG.

---

## 2. Pipeline des 4 agents

```
1. Collector Agent   → collecte les données brutes de coûts (Cost Explorer, CloudWatch)
        ↓
2. Analyzer Agent    → détecte les anomalies, ressources idle/oversized
        ↓
3. Forecaster Agent  → prédit les coûts des 30 prochains jours (Prophet)
        ↓
4. Recommender Agent → génère des recommandations en langage naturel (Bedrock / Claude 3 Sonnet)
```

**Orchestration** : LangGraph. Chaque agent écrit son résultat, l'agent suivant le lit.  
**Important** : c'est un pipeline séquentiel, pas des agents parallèles indépendants.

### Chatbot RAG (composant séparé)
Ne fait pas partie de la chaîne. Il interroge la base vectorielle OpenSearch (alimentée par les 4 agents) pour répondre aux questions utilisateur avec du contexte réel.

---

## 3. Flux de données

| Donnée | Stockage | Raison |
|---|---|---|
| Données brutes de coûts (CUR) | S3 + Athena | Gros volumes, requêtable en SQL |
| Métriques CloudWatch (CPU, RAM, réseau) | CloudWatch direct | Contexte technique pour expliquer une anomalie |
| Résumés / anomalies / recommandations | OpenSearch (vectoriel, Titan Embeddings) | Recherche sémantique pour le RAG |
| Secrets et clés API | AWS Secrets Manager | Sécurité |

---

## 4. Stack technique

### Infrastructure AWS (sandbox, Free Tier, budget ~20$/mois)
- **EC2** (t2.micro) — instances de démo
- **RDS** (db.t3.micro, MySQL) — base de données de démo
- **S3** — stockage CUR, logs, bucket de démo
- **Lambda** — fonctions de traitement (collector, analyzer, alerter)
- **Cost Explorer** — source principale des données de coûts
- **CloudWatch** — métriques complémentaires (CPU, réseau)
- **EventBridge** — déclenchement automatique (collecte toutes les 24h)
- **Athena** — requêtage SQL sur les CUR stockés en S3
- **Secrets Manager** — gestion des clés API
- **Bedrock (Claude 3 Sonnet)** — LLM pour les recommandations
- **Titan Embeddings** — vectorisation pour le RAG
- **OpenSearch** — base vectorielle pour le RAG
- **Cognito** — authentification du dashboard

### Intelligence Artificielle
- **LangGraph** — orchestration du workflow multi-agent
- **LangChain** — abstraction LLM + RAG
- **Prophet** — prévision de coûts (séries temporelles)
- **Scikit-learn (IsolationForest)** — détection d'anomalies

### Backend
- **Spring Boot (Java)** — API REST (`/analyze`, `/forecast`, `/chat`, `/report`)
- **Docker** — conteneurisation
- **ECS Fargate** — déploiement de l'agent

### Frontend
- **Angular** — dashboard web
- **Chart.js** — graphes (coûts, prévisions)
- **Angular Material** — composants UI

### Notifications
- **SNS + Slack Webhook** — alertes automatiques
- **ReportLab** — rapport PDF hebdomadaire

---

## 5. Infra de démonstration

Ressources déployées sur le compte sandbox pour générer des données réelles à analyser :

| Ressource | Détail |
|---|---|
| EC2 | 3 instances t2.micro (eu-north-1) |
| RDS | 1 instance db.t3.micro MySQL (`finops-db`) |
| S3 | 3 buckets : `finops-cur-data-louay`, `finops-logs-louay`, `finops-forgotten-louay` |
| Lambda | 3 fonctions Python 3.12 : `finops-collector`, `finops-analyzer`, `finops-alerter` |

Complétée par des datasets CUR synthétiques générés en Python pour simuler des scénarios d'anomalies.

---

## 6. Choix techniques justifiés

| Choix | Raison |
|---|---|
| LangGraph plutôt que LangChain seul | Gestion native du flux séquentiel entre agents |
| Bedrock plutôt qu'API Anthropic directe | Reste dans l'écosystème AWS, facturation centralisée, accès IAM |
| Prophet pour la prévision | Bibliothèque éprouvée pour les séries temporelles, simple à intégrer |
| IsolationForest pour les anomalies | Algorithme non supervisé, pas besoin de données labellisées |
| Spring Boot pour l'API | Contrainte de stack entreprise (Altran Telnet) |
| OpenSearch pour le RAG | Service managé AWS, intégration native avec Titan Embeddings |

---

## 7. Environnement de développement

- **OS** : macOS (Mac M4, Tahoe)
- **Python** : 3.12 via Homebrew
- **Venv** : `/Stage 4eme - FinOps Agent/venv`
- **Librairies** : boto3, langchain, langgraph
- **AWS CLI** : configuré avec l'utilisateur IAM `finops-agent-dev` (eu-north-1)
- **Repo Git** : https://github.com/louaycodes/finops-agent

---

## 8. Plan de sprints

| Sprint | Semaines | Livrable principal |
|---|---|---|
| Sprint 0 | 1-2 | Setup infra sandbox + environnement dev + ce document |
| Sprint 1 | 3-4 | Collector Agent + Analyzer Agent |
| Sprint 2 | 5-6 | Forecaster Agent + Recommender Agent + RAG |
| Sprint 3 | 7-8 | API Spring Boot + Dashboard Angular + Alertes |
