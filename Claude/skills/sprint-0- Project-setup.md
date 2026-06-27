---
name: sprint-0-setup
description: Utiliser ce skill quand on travaille sur le Sprint 0 du projet FinOps AI Agent — création du compte AWS sandbox, déploiement de la mini-infra de démo, génération des données synthétiques, et setup de l'environnement de développement (Python, Docker, LangChain, Bedrock). Déclencheurs — toute question sur la création du compte AWS, l'activation de Cost Explorer/CloudWatch, le déploiement initial d'EC2/RDS/S3/Lambda de démonstration, la génération de CUR synthétiques, ou l'installation de l'environnement local du projet.
---

# Sprint 0 — Setup & Architecture (Semaines 1-2)

## Objectif du sprint

Avoir une infrastructure AWS sandbox opérationnelle qui génère de vraies données de coûts, complétée par des données synthétiques, avec l'environnement de dev prêt à coder dessus.

## Ce qu'on construit, dans l'ordre logique

### 1. Compte AWS & sécurité de base
- Créer/utiliser un compte AWS dédié, ne **jamais** travailler avec le compte root pour le développement
- Créer un utilisateur IAM dédié avec permissions minimales (Cost Explorer read, CloudWatch read, EC2/S3/RDS/Lambda en lecture-écriture limitée au strict nécessaire)
- Configurer une alerte de budget AWS Billing à 20$ — étape non négociable avant toute autre action, pour éviter une mauvaise surprise

### 2. Activation des services de coûts
- Activer Cost Explorer (peut prendre jusqu'à 24h avant que les premières données apparaissent — c'est normal, ne pas chercher de bug si la liste est vide au tout début)
- Vérifier que CloudWatch collecte bien les métriques par défaut (CPU, réseau) sur toute ressource créée

### 3. Mini-infra de démo (la "cible" surveillée)
Déployer manuellement :
- 2-3 instances EC2 (t2.micro, Free Tier) — au moins une doit rester volontairement sous-utilisée pour générer une vraie anomalie "idle" plus tard
- 1 base RDS (db.t3.micro)
- 2-3 buckets S3 — dont un volontairement "oublié" (jamais accédé après création)
- 2-3 fonctions Lambda simples

Rappel : cette infra et le futur pipeline d'agents tournent sur le **même compte AWS** — ce n'est pas une infra séparée à surveiller à distance.

### 4. Données synthétiques (CUR)
Écrire un script Python qui génère un dataset de coûts réaliste pour enrichir les vraies données (qui seront limitées au début) :
- Format CUR standard ou simplifié (date, service, coût, ressource_id)
- Patterns réalistes : pics en semaine, creux le week-end
- Anomalies volontaires intégrées : un service dont le coût explose un mois donné, une ressource avec un pattern de gaspillage clair

### 5. Environnement de développement local
- Python 3.11+, environnement virtuel dédié au projet
- AWS CLI configuré avec les credentials du user IAM créé en étape 1
- Docker installé et fonctionnel
- `pip install langchain langgraph boto3`
- Demander l'accès à Amazon Bedrock (console Bedrock > Model access > activer Claude 3 Sonnet) — vérifier la région (Bedrock n'est pas disponible partout, privilégier us-east-1 si doute)

### 6. Documentation
- Rédiger un document d'architecture v1 (peut être un simple markdown avec le schéma du pipeline)
- Initialiser le repo Git

## Critère de fin de sprint

Un script Python tourne, appelle l'API Cost Explorer, et récupère des données réelles depuis le compte sandbox — même si les montants sont proches de zéro au début (Free Tier).

## Pièges connus de ce sprint

- **Cost Explorer vide au début** : délai de propagation, pas un bug
- **AccessDenied sur Bedrock** : modèle pas encore activé dans Model Access, ou mauvaise région
- **Budget qui dérape vite** : vérifier NAT Gateway, EBS non attachés, Elastic IP non associées — les pièges classiques du Free Tier

## En fin de sprint

Mettre à jour `01_TODO_SPRINTS.md` (cocher les tâches Sprint 0) et `05_ETAT_PROJET.md` (passer le statut à "Sprint 1" avec un résumé de ce qui a été fait).
