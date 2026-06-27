# Journal de Debug — FinOps AI Agent

> À chaque problème rencontré, ajoute une entrée. Ça permet à Claude de voir l'historique des erreurs déjà résolues et d'éviter de répéter les mêmes pistes.

---

## Comment utiliser ce fichier

Quand tu rencontres une erreur, donne à Claude :
1. Le message d'erreur complet (copier-coller, pas de résumé)
2. Le sprint et la tâche concernée (réfère-toi à `01_TODO_SPRINTS.md`)
3. Ce que tu as déjà essayé

Claude doit ensuite ajouter une entrée ici une fois le problème résolu, au format ci-dessous.

---

## Format d'une entrée

```
### [DATE] — [Sprint X] — Titre court du problème

**Contexte** : Qu'est-ce que tu essayais de faire
**Erreur** : Message d'erreur exact
**Cause** : Pourquoi ça arrivait
**Solution** : Ce qui a résolu le problème
**Statut** : ✅ Résolu / ⚠️ Contournement temporaire / ❌ Bloquant
```

---

## Entrées

*(vide pour l'instant — sera rempli au fil du stage)*

---

## Erreurs fréquentes connues à l'avance (FAQ rapide)

### "AccessDeniedException" sur Bedrock
→ Le modèle Claude n'est pas activé dans la console Bedrock pour ta région. Aller dans Bedrock > Model access > demander l'accès à Claude 3 Sonnet, attendre la validation (généralement instantanée mais peut prendre quelques minutes).

### Cost Explorer retourne une liste vide
→ Normal si le compte AWS vient d'être créé (délai de propagation jusqu'à 24h) ou si la période demandée est antérieure à l'activation de Cost Explorer.

### "ThrottlingException" sur les appels Bedrock
→ Tu dépasses le quota de requêtes par minute. Ajouter un retry avec backoff exponentiel, ou réduire la fréquence des appels en dev/test.

### Budget AWS qui augmente plus vite que prévu
→ Vérifier en premier : NAT Gateway (facturé à l'heure même si inutilisé), volumes EBS non attachés, snapshots oubliés, Elastic IP non associée. Ce sont les pièges classiques du Free Tier.

### LangGraph : un nœud du graphe ne reçoit pas le bon état
→ Vérifier le schéma d'état partagé (state) entre les nœuds — c'est l'erreur la plus commune en début d'implémentation LangGraph, souvent une clé mal nommée ou un type incompatible.

### OpenSearch : la recherche RAG retourne des résultats non pertinents
→ Vérifier que les embeddings sont bien générés avec le même modèle Titan pour l'indexation ET la requête (un mismatch de modèle d'embedding casse la similarité).

### Spring Boot ne arrive pas à appeler le pipeline Python
→ Vérifier d'abord l'ADR-05 dans `02_GLOSSAIRE_ET_ADR.md` — clarifier quel mode de communication a été choisi avant de débugger plus loin.
