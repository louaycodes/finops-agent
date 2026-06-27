---
name: sprint-1-collector-analyzer
description: Utiliser ce skill quand on travaille sur le Sprint 1 du projet FinOps AI Agent — développement du Collector Agent (collecte des coûts via Cost Explorer/CloudWatch, stockage S3/Athena, scheduling EventBridge) et de l'Analyzer Agent (détection d'anomalies avec Isolation Forest, scoring de criticité). Déclencheurs — toute question sur l'intégration de l'API Cost Explorer ou CloudWatch, le pipeline S3/Athena, la configuration EventBridge, la détection d'anomalies, les règles EC2 idle/S3 orphelin/RDS oversized, ou le scoring de criticité.
---

# Sprint 1 — Collector Agent + Analyzer Agent (Semaines 3-4)

## Objectif du sprint

Avoir un pipeline qui collecte automatiquement les coûts AWS et détecte les anomalies, classées par criticité.

## Prérequis

Le Sprint 0 doit être terminé : compte AWS sandbox actif, infra de démo déployée, environnement Python prêt. Si ce n'est pas le cas, rediriger vers le skill `sprint-0-setup` d'abord.

## Partie 1 — Collector Agent

### Collecte des données
- Module Python utilisant `boto3` pour appeler l'API **Cost Explorer** (`get_cost_and_usage`) — récupérer les coûts groupés par service et par jour
- Module séparé pour **CloudWatch Metrics** (`get_metric_data` ou `get_metric_statistics`) — CPU, mémoire (si agent CloudWatch installé), réseau, par ressource

### Stockage
- Normaliser les deux sources en un schéma de données commun (ex: `date, service, resource_id, cost_usd, cpu_avg, network_in, network_out`)
- Écrire les données au format **Parquet** dans S3 (plus efficace qu'un CSV pour Athena)
- Créer une table Athena pointant sur ce bucket S3, pour permettre le requêtage SQL ensuite

### Automatisation
- Configurer une règle **EventBridge** qui déclenche la fonction de collecte toutes les 24h (via Lambda ou un scheduler simple en dev)

### Test de validation
Le Collector doit produire au moins 7 jours de données cohérentes (mélange réel + synthétique) avant de passer à l'Analyzer.

## Partie 2 — Analyzer Agent

### Détection d'anomalies statistique
- Implémenter **Isolation Forest** (scikit-learn) sur les séries de coûts par service/ressource
- Le but : repérer les points qui s'écartent statistiquement du comportement normal

### Règles métier explicites (en complément du ML)
- **EC2 idle** : CPU moyen < 5% sur une fenêtre de 7 jours
- **S3 sans accès** : aucun accès enregistré depuis 30 jours
- **RDS oversized** : capacité provisionnée largement supérieure à l'usage observé

### Scoring de criticité
Définir une logique simple : High / Medium / Low, basée par exemple sur le montant économisable potentiel et la confiance de la détection.

### Test de validation
Faire tourner l'Analyzer sur les données contenant les anomalies volontaires injectées au Sprint 0 — vérifier qu'elles sont bien détectées (pas de faux négatif majeur) et correctement scorées.

## Critère de fin de sprint

Le pipeline Collector → Analyzer tourne automatiquement (déclenché par EventBridge) et produit une liste d'anomalies classées par criticité, stockée quelque part de consultable (S3/Athena ou simple fichier JSON en attendant le Sprint 2).

## Pièges connus de ce sprint

- **Permissions IAM insuffisantes** sur Cost Explorer/CloudWatch → vérifier la policy attachée à l'utilisateur
- **Trop peu de données pour Isolation Forest** → avec seulement quelques jours de données réelles, s'appuyer davantage sur les données synthétiques en complément pour avoir un volume suffisant
- **Faux positifs en masse** → si tout est détecté comme anomalie, vérifier les seuils des règles métier (souvent trop stricts au début)

## En fin de sprint

Mettre à jour `01_TODO_SPRINTS.md` (cocher les tâches Sprint 1) et `05_ETAT_PROJET.md` (passer le statut à "Sprint 2" avec un résumé de ce qui a été fait, et noter les seuils/paramètres choisis pour les règles de détection — utile pour le Sprint 2 et la documentation finale).
