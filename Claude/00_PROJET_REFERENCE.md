# FinOps AI Agent — Document de Référence du Projet

> **Ce fichier est la source de vérité du projet.** Claude doit le consulter en cas de doute sur l'architecture, le périmètre ou les choix techniques avant de répondre à une question de debug ou d'implémentation.

---

## 1. Identité du projet

| Champ | Valeur |
|---|---|
| Stagiaire | Louay Zorai |
| École | ESPRIT School of Engineering — ArcTIC, 4ème année |
| Entreprise | Altran Telnet Corporation |
| Durée | 2 mois |
| Sujet | Agent IA de FinOps pour l'optimisation intelligente des coûts AWS |

---

## 2. Le concept en une phrase

Un pipeline de 4 agents IA orchestrés par LangGraph qui collecte les **coûts AWS** (pas les métriques système classiques), détecte les anomalies de dépenses, prédit les coûts futurs, et génère des recommandations en langage naturel via Amazon Bedrock — le tout accessible via une API Spring Boot, un dashboard Angular, et un chatbot RAG.

---

## 3. Ce que ce projet N'EST PAS (erreurs de conception à éviter)

- **Ce n'est PAS un projet de monitoring système classique** (type Zabbix/Prometheus). CloudWatch (CPU/RAM) n'est qu'un signal complémentaire pour expliquer *pourquoi* une ressource coûte cher — la donnée centrale est le **coût en dollars** via Cost Explorer / CUR.
- **Ce n'est PAS 4 agents indépendants qui tournent en parallèle.** C'est un **pipeline séquentiel** : Collector → Analyzer → Forecaster → Recommender. Chaque agent dépend du résultat du précédent.
- **Le chatbot RAG n'est PAS un 5ème agent dans la chaîne.** C'est une interface séparée qui interroge ce que les 4 agents ont déjà produit et stocké dans OpenSearch.
- **L'infra de test n'est PAS une infra de production "empruntée".** Elle est construite de zéro sur un compte AWS sandbox personnel, complétée par des données synthétiques.
- **Le pipeline d'agents et l'infra surveillée tournent sur le MÊME compte AWS.** Pas deux comptes séparés — juste des ressources différentes dans le même environnement (analogie : la caméra de surveillance et la pièce surveillée sont dans la même maison).

---

## 4. Architecture — Le pipeline des 4 agents

```
1. Collector Agent   → récupère les données brutes de coûts (Cost Explorer, CloudWatch)
        ↓
2. Analyzer Agent    → détecte anomalies, ressources idle/oversized
        ↓
3. Forecaster Agent  → prédit les coûts des 30 prochains jours (Prophet)
        ↓
4. Recommender Agent → transforme analyse + prédiction en recommandations texte (Bedrock/Claude)
```

Orchestration : **LangGraph**. Chaque étape écrit son résultat, l'étape suivante le lit.

### Le chatbot RAG (composant séparé)
Ne fait PAS partie de la chaîne ci-dessus. Il interroge la base vectorielle OpenSearch (alimentée par les 4 agents) pour répondre aux questions utilisateur avec du contexte réel, au lieu de laisser le LLM deviner/halluciner.

---

## 5. Flux de données — où est stocké quoi et pourquoi

| Donnée | Stockage | Pourquoi |
|---|---|---|
| Données brutes de coûts (CUR) | S3 + Athena | Gros volumes, requêtable en SQL |
| Métriques CloudWatch (CPU, RAM, réseau) | CloudWatch direct | Contexte technique pour expliquer une anomalie de coût |
| Résumés / anomalies / recommandations en texte | OpenSearch (vectoriel, via Titan Embeddings) | Recherche sémantique pour le RAG |
| Configuration, secrets, clés API | AWS Secrets Manager | Sécurité |

---

## 6. Stack technique complet

### Infrastructure & Cloud (compte AWS sandbox, Free Tier, budget ~20$/mois)
- **AWS Lambda + ECS Fargate** — exécution de l'agent
- **S3 + Amazon Athena** — stockage et requêtage des Cost & Usage Reports
- **Amazon CloudWatch** — métriques de consommation par ressource
- **Amazon EventBridge** — déclenchement automatique (collecte toutes les 24h)
- **AWS Secrets Manager** — gestion sécurisée des clés API

### Intelligence Artificielle
- **Amazon Bedrock (Claude 3 Sonnet)** — LLM pour les recommandations en langage naturel
- **Amazon Titan Embeddings** — vectorisation pour le RAG
- **LangGraph** — orchestration du workflow multi-agent
- **LangChain + OpenSearch** — RAG (recherche sémantique sur l'historique)
- **Prophet (Python)** — prévision de coûts (séries temporelles)
- **Scikit-learn (IsolationForest)** — détection statistique d'anomalies

### Backend
- **Spring Boot (Java)** — API REST exposant l'agent
- **Docker** — conteneurisation
- **AWS Cognito** — authentification du dashboard

### Frontend
- **Angular** — dashboard web
- **Chart.js** — graphes (coûts, prévisions)
- **Angular Material** — composants UI

### Notifications & Rapports
- **SNS + Slack Webhook** — alertes automatiques
- **ReportLab** — rapport PDF hebdomadaire (généré côté Python)

---

## 7. Infra de démonstration (ce qui génère les coûts à analyser)

Mini-infra à déployer sur le compte sandbox :
- 2-3 instances EC2 (t2.micro, Free Tier)
- 1 base RDS
- Plusieurs buckets S3
- Quelques fonctions Lambda

Complétée par des **datasets CUR synthétiques** générés en Python pour simuler des scénarios d'anomalies que la mini-infra réelle ne produirait pas naturellement (pics de coûts, ressources oubliées, etc.).

---

## 8. Plan de travail — 4 sprints de 2 semaines

### Sprint 0 (Semaines 1-2) — Setup & Architecture
- Créer le compte AWS sandbox + activer Cost Explorer, CloudWatch, budget alert à 20$
- Déployer la mini-infra de démo (EC2, RDS, S3, Lambda)
- Générer les premiers datasets CUR synthétiques (script Python)
- Setup environnement local : Python, Docker, AWS CLI, LangChain, LangGraph
- Demander l'accès Amazon Bedrock (quotas Claude 3 Sonnet)
- Rédiger le document d'architecture v1

**Livrable** : infra sandbox opérationnelle + données de coûts disponibles + doc architecture v1

---

### Sprint 1 (Semaines 3-4) — Collector Agent + Analyzer Agent
- Intégration AWS Cost Explorer API (coûts par service/jour)
- Intégration CloudWatch Metrics (CPU, mémoire, réseau)
- Pipeline S3 + Athena (parser CUR au format Parquet, requêtage SQL)
- Scheduler EventBridge (collecte automatique toutes les 24h)
- Algorithme de détection d'anomalies (Isolation Forest)
- Règles de détection : EC2 idle (CPU < 5%), S3 sans accès depuis 30j, RDS oversized
- Scoring de criticité (High / Medium / Low)

**Livrable** : Collector Agent fonctionnel + Analyzer Agent qui détecte/classe les anomalies sur les données sandbox

---

### Sprint 2 (Semaines 5-6) — Forecaster Agent + Recommender Agent (Bedrock + RAG)
- Modèle Prophet sur l'historique de coûts (prévision 30 jours)
- Premiers appels Amazon Bedrock (Claude 3 Sonnet)
- Vectorisation des données (Titan Embeddings → OpenSearch)
- Architecture RAG complète (LangChain + OpenSearch)
- Recommender Agent : génération de recommandations en langage naturel
- Chaînage LangGraph des 4 agents (workflow end-to-end)
- Prompt engineering + tests de qualité des outputs LLM

**Livrable** : prévisions de coûts générées + workflow 4-agents end-to-end fonctionnel + recommandations textuelles

---

### Sprint 3 (Semaines 7-8) — API + Dashboard + Alertes + Finalisation
- Backend Spring Boot : endpoints `/analyze`, `/forecast`, `/chat`, `/report`
- Chatbot conversationnel avec mémoire de session
- Déploiement Docker sur ECS Fargate
- Dashboard Angular : pages Overview, Anomalies, Forecast, Chat
- Auth Cognito + intégration dashboard ↔ API
- Système d'alertes SNS → Slack
- Génération rapport PDF hebdomadaire (ReportLab)
- Tests end-to-end + documentation complète (README, ADR, guide de déploiement)
- Préparation démo finale + rédaction rapport de stage

**Livrable** : API déployée sur AWS + dashboard Angular complet + alertes fonctionnelles + rapport de stage

**Priorités si le temps manque (du plus au moins critique)** :
1. API Spring Boot + déploiement (indispensable)
2. Dashboard Angular avec les 4 pages (indispensable pour la démo)
3. Chatbot fonctionnel (cœur de la valeur ajoutée)
4. Alertes Slack (simplifiable)
5. Rapport PDF auto (peut être fait manuellement une fois si besoin)

---

## 9. Livrables finaux attendus

| Code | Livrable | Détail |
|---|---|---|
| L1 | Agent IA multi-composants | Workflow LangGraph complet, 4 sous-agents opérationnels |
| L2 | API REST Spring Boot | Endpoints `/analyze`, `/forecast`, `/chat`, `/report` déployés sur ECS Fargate |
| L3 | Dashboard Angular | Overview, prévisions, anomalies, chatbot, auth Cognito |
| L4 | Système d'alertes & rapports | Alertes Slack + rapport PDF hebdomadaire |
| L5 | Documentation technique | ADR, guide de déploiement, README, rapport de stage |

---

## 10. Règles de communication avec Claude pour ce projet

- Toujours répondre en **français**, de manière **brève et précise** (préférence utilisateur)
- Avant de proposer une solution de debug, vérifier la cohérence avec l'architecture décrite ci-dessus
- Ne jamais suggérer de pivoter vers une stack différente (ex: FastAPI au lieu de Spring Boot, React au lieu d'Angular) sans que ce soit explicitement demandé
- Toujours rappeler qu'on travaille sur un compte **sandbox**, pas en production — donc privilégier les solutions économes en coûts AWS (Free Tier, petites instances)
- Si une erreur AWS apparaît, toujours vérifier en premier : permissions IAM, région AWS, quotas Bedrock, budget dépassé
