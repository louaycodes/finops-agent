# TODO Détaillée — Suivi de Progression par Sprint

> Coche les cases au fur et à mesure. Demande à Claude de mettre à jour ce fichier quand une tâche est terminée, pour garder une trace de l'avancement réel.

**Statut global du projet** : 🟦 En cours — Sprint 0

---

## 🟦 SPRINT 0 — Setup & Architecture (Semaines 1-2)

### Compte AWS & infra de démo
- [x] Créer un compte AWS (ou utiliser un compte existant) dédié au sandbox
- [x] Configurer une alerte de budget AWS Billing à 20$
- [x] Activer AWS Cost Explorer
- [x] Activer AWS CloudWatch (par défaut, vérifier les rétentions de logs)
- [x] Créer un utilisateur IAM dédié au projet (ne pas utiliser le compte root)
- [x] Définir les permissions IAM minimales nécessaires (principe du moindre privilège)
- [x] Déployer 2-3 instances EC2 (t2.micro, Free Tier)
- [x] Déployer une base RDS (db.t3.micro si possible)
- [x] Créer 2-3 buckets S3 (un pour les données CUR, un pour les logs, un "oublié" pour simuler une anomalie)
- [x] Déployer 2-3 fonctions Lambda simples

### Données synthétiques
- [ ] Écrire un script Python générant des données CUR synthétiques réalistes
- [ ] Inclure des patterns réalistes (pics le lundi, creux le week-end)
- [ ] Inclure des anomalies volontaires (une ressource dont le coût explose un mois donné)

### Environnement de développement
- [x] Installer Python 3.11+ et créer un environnement virtuel
- [x] Installer AWS CLI et configurer les credentials
- [ ] Installer Docker
- [x] Installer LangChain, LangGraph (`pip install langchain langgraph`)
- [x] Installer boto3 (SDK AWS Python)
- [x] Demander l'accès à Amazon Bedrock (région supportée, modèle Claude 3 Sonnet activé)
- [x] Vérifier les quotas Bedrock disponibles

### Documentation
- [ ] Rédiger le document d'architecture v1 (diagramme + choix techniques)
- [ ] Initialiser le repo Git du projet

**Critère de fin de sprint** : tu peux lancer un script Python qui appelle Cost Explorer et récupère des données réelles depuis ton compte sandbox.

---

## 🟦 SPRINT 1 — Collector Agent + Analyzer Agent (Semaines 3-4)

### Collector Agent
- [ ] Écrire le module d'appel à l'API Cost Explorer (coûts par service, par jour)
- [ ] Écrire le module d'appel à CloudWatch Metrics (CPU, mémoire, réseau par ressource)
- [ ] Définir le schéma de données normalisé (format commun pour stocker les coûts)
- [ ] Convertir/stocker les données au format Parquet dans S3
- [ ] Créer la table Athena pour requêter les données S3 en SQL
- [ ] Configurer EventBridge pour déclencher la collecte toutes les 24h
- [ ] Tester la collecte sur au moins 7 jours de données (réelles + synthétiques)

### Analyzer Agent
- [ ] Implémenter la détection d'anomalies avec Isolation Forest (scikit-learn)
- [ ] Implémenter la règle "EC2 idle" (CPU moyen < 5% sur 7 jours)
- [ ] Implémenter la règle "S3 sans accès" (pas d'accès depuis 30 jours)
- [ ] Implémenter la règle "RDS oversized" (capacité largement sous-utilisée)
- [ ] Définir le système de scoring de criticité (High / Medium / Low)
- [ ] Tester l'Analyzer sur les données avec anomalies volontaires
- [ ] Vérifier que les vraies anomalies sont bien détectées (pas de faux négatifs majeurs)

**Critère de fin de sprint** : le pipeline Collector → Analyzer tourne automatiquement et produit une liste d'anomalies classées par criticité.

---

## 🟦 SPRINT 2 — Forecaster Agent + Recommender Agent (Semaines 5-6)

### Forecaster Agent
- [ ] Préparer les données pour Prophet (format date/valeur)
- [ ] Entraîner un premier modèle Prophet sur l'historique de coûts
- [ ] Générer une prévision à 30 jours
- [ ] Valider la qualité de la prévision (comparer avec un historique connu)

### Bedrock & RAG
- [ ] Obtenir et tester le premier appel à Amazon Bedrock (Claude 3 Sonnet)
- [ ] Configurer Amazon Titan Embeddings
- [ ] Mettre en place une instance/index OpenSearch
- [ ] Vectoriser les résultats de l'Analyzer (anomalies) et les stocker dans OpenSearch
- [ ] Construire la chaîne RAG avec LangChain (retrieval + génération)
- [ ] Tester une première requête RAG (poser une question, vérifier que le contexte récupéré est pertinent)

### Recommender Agent
- [ ] Écrire le prompt système pour générer des recommandations à partir d'une anomalie
- [ ] Connecter le Recommender à Bedrock
- [ ] Tester la génération de recommandations sur 5-10 anomalies différentes
- [ ] Itérer sur le prompt si les recommandations sont vagues ou incorrectes

### Orchestration LangGraph
- [ ] Définir le graphe LangGraph (les 4 nœuds + les transitions)
- [ ] Tester le workflow complet end-to-end (Collector → Analyzer → Forecaster → Recommender)
- [ ] Gérer les cas d'erreur (un agent qui échoue ne doit pas planter tout le pipeline)

**Critère de fin de sprint** : en lançant une seule commande, le pipeline complet s'exécute et produit des recommandations textuelles + une prévision de coûts.

---

## 🟦 SPRINT 3 — API + Dashboard + Alertes + Finalisation (Semaines 7-8)

### API Spring Boot
- [ ] Initialiser le projet Spring Boot (Spring Initializr : Web, Security si besoin)
- [ ] Créer l'endpoint `POST /analyze`
- [ ] Créer l'endpoint `GET /forecast`
- [ ] Créer l'endpoint `POST /chat`
- [ ] Créer l'endpoint `GET /report`
- [ ] Définir comment Spring Boot communique avec le pipeline Python (appel de script, API interne Python/FastAPI en sidecar, ou lecture directe S3/OpenSearch — à trancher tôt)
- [ ] Documenter l'API (Swagger/OpenAPI)
- [ ] Containeriser l'API avec Docker
- [ ] Déployer le conteneur sur ECS Fargate
- [ ] Tester les endpoints en production (Postman/curl)

### Chatbot
- [ ] Ajouter la gestion de mémoire de session côté chaîne RAG (LangChain Memory)
- [ ] Connecter l'endpoint `/chat` à la chaîne RAG
- [ ] Tester une conversation multi-tours

### Dashboard Angular
- [ ] Initialiser le projet Angular (Angular CLI)
- [ ] Installer Angular Material + Chart.js
- [ ] Page Overview (coûts totaux, top 5 services, tendance)
- [ ] Page Anomalies (liste, criticité, recommandation associée)
- [ ] Page Forecast (graphe de prévision 30 jours)
- [ ] Page Chat (interface conversationnelle)
- [ ] Connecter chaque page aux endpoints Spring Boot
- [ ] Configurer AWS Cognito et l'authentification côté Angular

### Alertes & Rapports
- [ ] Configurer SNS pour les alertes de dépassement de seuil
- [ ] Connecter SNS à un webhook Slack
- [ ] Définir les seuils d'alerte par service
- [ ] Écrire le script de génération de rapport PDF (ReportLab)
- [ ] Automatiser la génération hebdomadaire (EventBridge + Lambda)

### Finalisation
- [ ] Tests end-to-end du parcours complet (collecte → dashboard → chatbot)
- [ ] Rédiger le README du projet
- [ ] Rédiger les Architecture Decision Records (ADR)
- [ ] Rédiger le guide de déploiement
- [ ] Préparer 2-3 scénarios de démo concrets pour la soutenance
- [ ] Rédiger le rapport de stage

**Critère de fin de sprint** : démo complète possible — montrer une anomalie détectée, sa recommandation, la prévision de coûts, et poser une question au chatbot dessus.

---

## 📝 Notes de suivi (à compléter au fil du stage)

| Date | Sprint | Note |
|---|---|---|
| | | |
