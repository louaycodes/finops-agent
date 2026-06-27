---
name: sprint-2-forecast-rag
description: Utiliser ce skill quand on travaille sur le Sprint 2 du projet FinOps AI Agent — développement du Forecaster Agent (prévision de coûts avec Prophet), intégration d'Amazon Bedrock et Titan Embeddings, mise en place du RAG avec LangChain et OpenSearch, développement du Recommender Agent, et chaînage complet du workflow avec LangGraph. Déclencheurs — toute question sur Prophet/séries temporelles, les appels Bedrock/Claude 3, les Titan Embeddings, OpenSearch, l'architecture RAG, le prompt engineering pour les recommandations, ou l'orchestration LangGraph du pipeline complet.
---

# Sprint 2 — Forecaster Agent + Recommender Agent (Bedrock + RAG) (Semaines 5-6)

## Objectif du sprint

Ajouter la capacité de prédiction et de génération de langage naturel au pipeline, et brancher le RAG qui alimentera le futur chatbot.

## Prérequis

Le Sprint 1 doit être terminé : Collector et Analyzer fonctionnels, anomalies détectées et stockées. Si ce n'est pas le cas, rediriger vers `sprint-1-collector-analyzer` d'abord.

## Partie 1 — Forecaster Agent

- Préparer les données issues du Collector au format attendu par **Prophet** (colonnes `ds` pour la date, `y` pour la valeur — ici le coût)
- Entraîner un modèle Prophet par service (ou globalement, selon la granularité voulue)
- Générer une prévision à 30 jours
- Valider la qualité : comparer la prévision à un historique connu si possible, ou au minimum vérifier que les tendances générées sont cohérentes (pas de valeurs aberrantes ou négatives)

## Partie 2 — Bedrock & Titan Embeddings

- Premier appel à **Amazon Bedrock** avec Claude 3 Sonnet (`invoke_model` via boto3, ou le client Bedrock Runtime)
- Configurer **Titan Embeddings** pour vectoriser du texte
- Tester un cycle complet : texte → embedding → vérifier la dimension du vecteur retourné

## Partie 3 — RAG (LangChain + OpenSearch)

- Mettre en place une instance ou un index OpenSearch (privilégier OpenSearch Serverless avec la capacité minimale pour limiter les coûts sandbox)
- Vectoriser les résultats de l'Analyzer (les anomalies détectées au Sprint 1) et les indexer dans OpenSearch
- Construire la chaîne RAG avec LangChain : retrieval (recherche des documents pertinents) puis génération (Bedrock répond avec ce contexte)
- Tester une première requête : poser une question sur une anomalie connue, vérifier que le contexte récupéré est bien le bon avant même de regarder la réponse générée

**Point d'attention important** : le modèle d'embedding utilisé pour indexer doit être strictement le même que celui utilisé pour interroger — un mismatch casse silencieusement la pertinence de la recherche.

## Partie 4 — Recommender Agent

- Écrire le prompt système : à partir d'une anomalie (avec son contexte, sa criticité, et idéalement la prévision associée), générer une recommandation actionnable en langage naturel
- Connecter à Bedrock
- Tester sur 5-10 anomalies différentes pour vérifier la qualité et la variété des recommandations
- Itérer sur le prompt si les réponses sont vagues, génériques, ou factuellement incorrectes

## Partie 5 — Orchestration LangGraph

- Définir le graphe : 4 nœuds (Collector, Analyzer, Forecaster, Recommender) + les transitions entre eux
- Définir un schéma d'état partagé clair (quelles clés transitent entre les nœuds — c'est la source d'erreur la plus fréquente à ce stade)
- Tester le workflow complet en une seule commande
- Gérer les erreurs : un agent qui échoue ne doit pas faire planter tout le pipeline (prévoir un comportement de repli ou un statut d'erreur propagé)

## Critère de fin de sprint

En lançant une seule commande, le pipeline des 4 agents s'exécute de bout en bout et produit : une prévision de coûts à 30 jours + des recommandations textuelles pour chaque anomalie détectée.

## Pièges connus de ce sprint

- **ThrottlingException sur Bedrock** : quota de requêtes par minute dépassé, ajouter un retry avec backoff exponentiel
- **LangGraph : état mal transmis entre nœuds** : vérifier les noms de clés et les types dans le schéma d'état partagé
- **RAG qui retourne des résultats non pertinents** : vérifier la cohérence du modèle d'embedding entre indexation et requête

## En fin de sprint

Mettre à jour `01_TODO_SPRINTS.md` (cocher les tâches Sprint 2) et `05_ETAT_PROJET.md` (passer le statut à "Sprint 3", noter les prompts finaux retenus pour le Recommender — utiles pour la documentation et la soutenance).
