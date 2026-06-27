---
name: sprint-3-api-dashboard
description: Utiliser ce skill quand on travaille sur le Sprint 3 du projet FinOps AI Agent — développement de l'API Spring Boot, du chatbot conversationnel, déploiement Docker/ECS Fargate, dashboard Angular (Overview, Anomalies, Forecast, Chat), authentification Cognito, alertes SNS/Slack, rapport PDF, et finalisation (tests, documentation, préparation soutenance). Déclencheurs — toute question sur les endpoints Spring Boot, l'intégration Angular, Cognito, Docker/ECS Fargate, les alertes Slack, la génération de rapport PDF, ou la préparation du rapport de stage et de la démo finale.
---

# Sprint 3 — API + Dashboard + Alertes + Finalisation (Semaines 7-8)

## Objectif du sprint

Transformer le pipeline d'agents (fonctionnel depuis le Sprint 2) en un produit démontrable : API exposée, dashboard utilisable, alertes actives, documentation prête pour la soutenance.

## Prérequis

Le Sprint 2 doit être terminé : pipeline LangGraph complet et fonctionnel end-to-end. Si ce n'est pas le cas, rediriger vers `sprint-2-forecast-rag` d'abord.

## Décision préalable à trancher en premier (ADR-05)

Avant de coder l'API, clarifier comment Spring Boot communique avec le pipeline Python. Voir `02_GLOSSAIRE_ET_ADR.md` ADR-05. Recommandation : lecture directe des résultats déjà calculés (S3/OpenSearch) pour `/forecast` et `/report`, appel HTTP vers un service Python séparé pour `/chat` (interaction temps réel avec le RAG).

## Partie 1 — API Spring Boot

- Initialiser le projet (Spring Initializr — dépendances Web, et Security si l'auth est gérée côté Spring)
- Endpoints à créer :
  - `POST /analyze` — déclenche une analyse à la demande
  - `GET /forecast` — retourne la prévision 30 jours
  - `POST /chat` — envoie une question au chatbot RAG
  - `GET /report` — récupère le rapport PDF généré
- Documenter l'API avec Swagger/OpenAPI
- Containeriser avec Docker (Dockerfile multi-stage recommandé pour limiter la taille de l'image)
- Déployer sur ECS Fargate
- Tester chaque endpoint en conditions réelles (Postman ou curl) une fois déployé

## Partie 2 — Chatbot conversationnel

- Ajouter la gestion de mémoire de session à la chaîne RAG (LangChain Memory) pour que le chatbot garde le contexte d'une conversation
- Connecter l'endpoint `/chat` à cette chaîne
- Tester une conversation à plusieurs tours pour vérifier que le contexte est bien conservé

## Partie 3 — Dashboard Angular

- Initialiser le projet (Angular CLI), installer Angular Material et Chart.js
- 4 pages à construire :
  - **Overview** — coûts totaux, top 5 services, courbe de tendance
  - **Anomalies** — liste avec criticité et recommandation associée
  - **Forecast** — graphe de prévision 30 jours (Chart.js)
  - **Chat** — interface conversationnelle connectée à `/chat`
- Connecter chaque page aux endpoints Spring Boot correspondants
- Configurer AWS Cognito pour l'authentification côté Angular

## Partie 4 — Alertes & Rapports

- Configurer SNS pour déclencher une alerte sur dépassement de seuil de coût
- Connecter SNS à un webhook Slack
- Définir les seuils par service (peuvent être simples au départ, ex: seuil fixe en dollars)
- Écrire le script de génération de rapport PDF avec ReportLab (résumé hebdomadaire : coûts, anomalies, recommandations)
- Automatiser la génération hebdomadaire (EventBridge + Lambda, ou script planifié simple si le temps manque)

## Partie 5 — Finalisation

- Tests end-to-end du parcours complet : collecte → analyse → dashboard → chatbot
- Rédiger le README du projet
- Rédiger les Architecture Decision Records (s'appuyer sur `02_GLOSSAIRE_ET_ADR.md` comme base)
- Rédiger le guide de déploiement
- Préparer 2-3 scénarios de démo concrets (ex: montrer une anomalie détectée, sa recommandation, puis demander au chatbot de l'expliquer)
- Rédiger le rapport de stage

## Priorités si le temps manque (ce sprint est dense)

1. API Spring Boot + déploiement — indispensable
2. Dashboard Angular avec les 4 pages — indispensable pour la démo
3. Chatbot fonctionnel — cœur de la valeur ajoutée
4. Alertes Slack — simplifiable (peut rester basique)
5. Rapport PDF auto — peut être généré manuellement une fois si le temps manque vraiment

## Critère de fin de sprint

Démo complète possible : montrer une anomalie détectée sur le dashboard, sa recommandation générée, la prévision de coûts associée, et poser une question dessus au chatbot — sans bug bloquant.

## Pièges connus de ce sprint

- **Spring Boot n'arrive pas à appeler le pipeline Python** : revenir d'abord à l'ADR-05, clarifier le mode de communication choisi avant de débugger plus loin
- **Déploiement ECS Fargate qui échoue** : vérifier les permissions IAM du rôle de tâche, et que l'image Docker est bien poussée sur un registre accessible (ECR)
- **Cognito mal configuré côté Angular** : vérifier le pool d'utilisateurs et le client app ID correspondent bien entre AWS et la config Angular

## En fin de sprint

Mettre à jour `01_TODO_SPRINTS.md` (cocher les tâches Sprint 3) et `05_ETAT_PROJET.md` (marquer le projet comme terminé, avec un résumé global final — utile pour relire avant la soutenance).
