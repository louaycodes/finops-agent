# Journal de Debug — Mode d'Emploi

> Ce fichier contient uniquement les instructions et la FAQ de référence. **Il ne doit jamais contenir d'entrées de bugs réels** — celles-ci vont exclusivement dans `03_JOURNAL_DEBUG_ENTRIES.md`. Claude ne doit jamais écrire d'entrée de bug dans ce fichier-ci.

---

## Comment ça fonctionne

Quand un bug est rencontré et résolu dans une conversation, Claude doit :
1. Ouvrir `03_JOURNAL_DEBUG_ENTRIES.md` (PAS ce fichier-ci)
2. Ajouter une nouvelle entrée à la fin, au format défini ci-dessous
3. Sauvegarder le fichier

L'utilisateur (Louay), de son côté, donne à Claude :
1. Le message d'erreur complet (copier-coller, pas de résumé)
2. Le sprint et la tâche concernée (réfère-toi à `01_TODO_SPRINTS.md`)
3. Ce qui a déjà été essayé

---

## Format d'une entrée (à utiliser dans `03_JOURNAL_DEBUG_ENTRIES.md`)

```
### [DATE] — [Sprint X] — Titre court du problème

**Contexte** : Qu'est-ce que tu essayais de faire
**Erreur** : Message d'erreur exact
**Cause** : Pourquoi ça arrivait
**Solution** : Ce qui a résolu le problème
**Statut** : ✅ Résolu / ⚠️ Contournement temporaire / ❌ Bloquant
```

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
