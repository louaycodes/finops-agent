# Glossaire Technique & Décisions d'Architecture

> Référence rapide pour Claude et pour Louay — évite de re-expliquer les mêmes concepts à chaque conversation.

---

## Glossaire des termes clés

| Terme | Définition dans le contexte du projet |
|---|---|
| **CUR** | Cost & Usage Report — le rapport détaillé de facturation AWS, format brut des données de coûts |
| **Cost Explorer** | Service AWS qui donne une vue agrégée et requêtable des coûts par service/période |
| **FinOps** | Pratique de gestion financière du cloud — optimiser les coûts sans sacrifier la performance |
| **RAG** | Retrieval-Augmented Generation — au lieu de laisser le LLM répondre de mémoire, on va chercher des données pertinentes (via recherche vectorielle) et on les injecte dans le prompt |
| **Embedding** | Représentation numérique (vecteur) d'un texte, permettant de mesurer la similarité sémantique entre deux contenus |
| **LangGraph** | Framework pour orchestrer des workflows multi-étapes avec des LLM (chaque étape = un nœud du graphe) |
| **Isolation Forest** | Algorithme de machine learning non supervisé pour détecter les anomalies (points qui s'isolent statistiquement du reste) |
| **Prophet** | Librairie de Facebook/Meta pour la prévision de séries temporelles (utilisée ici pour prédire les coûts futurs) |
| **ECS Fargate** | Service AWS pour exécuter des conteneurs Docker sans gérer de serveurs |
| **Idle resource** | Ressource AWS payée mais quasiment inutilisée (ex: EC2 avec CPU < 5%) |
| **Oversized resource** | Ressource dimensionnée plus grande que nécessaire par rapport à son usage réel |

---

## Décisions d'architecture (ADR résumés)

### ADR-01 — Pourquoi un pipeline séquentiel et non des agents parallèles ?
**Décision** : Collector → Analyzer → Forecaster → Recommender en chaîne.
**Raison** : Chaque étape a besoin du résultat de la précédente (l'Analyzer a besoin des données collectées, le Recommender a besoin de l'analyse ET de la prévision). Un système parallèle compliquerait inutilement la synchronisation.

### ADR-02 — Pourquoi séparer le chatbot RAG du pipeline principal ?
**Décision** : Le chatbot est une interface à la demande, pas une étape automatique du pipeline.
**Raison** : Le pipeline tourne sur un planning fixe (toutes les 24h) et produit des données. Le chatbot répond à des questions ponctuelles de l'utilisateur, à tout moment — ce sont deux besoins différents (batch vs interactif).

### ADR-03 — Pourquoi un compte AWS sandbox plutôt que la prod Altran Telnet ?
**Décision** : Infra de démo construite sur un compte personnel Free Tier.
**Raison** : Pas d'accès donné par l'entreprise pour des raisons de sécurité/confidentialité (normal pour un stagiaire). L'architecture du code reste identique — seules les credentials AWS changeraient pour pointer vers une vraie infra plus tard.

### ADR-04 — Pourquoi stocker les données brutes dans S3/Athena ET les résumés dans OpenSearch ?
**Décision** : Deux systèmes de stockage différents pour deux usages différents.
**Raison** : S3/Athena est optimisé pour de gros volumes de données structurées interrogeables en SQL (les CUR). OpenSearch est optimisé pour la recherche sémantique (vecteurs) nécessaire au RAG. Mélanger les deux usages dans un seul système serait inefficace.

### ADR-05 — Comment Spring Boot communique avec le pipeline Python ?
**Décision à prendre tôt dans le Sprint 3** (encore ouverte) — options possibles :
1. Spring Boot appelle un script Python en sous-processus (simple mais fragile)
2. Le pipeline Python tourne comme un service séparé (FastAPI interne) que Spring Boot appelle en HTTP (recommandé — propre et découplé)
3. Spring Boot lit directement les résultats déjà écrits dans S3/OpenSearch par le pipeline Python (le pipeline tourne de façon autonome via EventBridge, Spring Boot ne fait que lire)

**Recommandation** : Option 3 pour les endpoints `/forecast` et `/report` (lecture de résultats déjà calculés), Option 2 pour `/chat` (interaction temps réel nécessaire avec le RAG).

---

## Pièges classiques à anticiper

| Risque | Symptôme | Piste de résolution |
|---|---|---|
| Quota Bedrock non activé | Erreur 403/AccessDenied sur les appels Claude | Vérifier la demande d'accès au modèle dans la console Bedrock, région correcte |
| Coûts sandbox qui dérapent | Alerte budget AWS déclenchée | Vérifier les ressources non Free Tier laissées actives (NAT Gateway, EBS non attaché, etc.) |
| Cost Explorer données vides au début | Pas de données sur les premiers jours | Cost Explorer a un délai de mise à jour (jusqu'à 24h) — normal en tout début de sprint 0 |
| Permissions IAM insuffisantes | Erreur AccessDenied sur Cost Explorer/CloudWatch | Vérifier la policy IAM attachée à l'utilisateur/rôle utilisé |
| OpenSearch coûteux si mal dimensionné | Facture qui grimpe vite | Utiliser OpenSearch Serverless avec les plus petites capacités, ou une alternative légère en dev (ex: FAISS local) si le budget est serré |
| Région AWS incohérente | Bedrock ou un service indisponible | Vérifier que tous les services utilisés sont bien déployés dans la même région (ex: us-east-1) |
