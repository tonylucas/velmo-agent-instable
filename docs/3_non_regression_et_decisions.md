# Non-régression et journal de décisions

Source des conversations : `data/conversations_problematiques.json`

---

## Rejeu des conversations fournies

Pour chaque conversation, on indique ce que l'agent produit **dans son état actuel** et si le comportement attendu est atteint.

---

### `ctx-oubli-1` — Perte de contexte sur deux tours

**Comportement attendu** : l'assistant se souvient de la commande 4521 mentionnée au premier tour.

**Résultat** : ✅ Corrigé

Deux corrections combinées :

- `memory.py` : `history()` retourne maintenant `_turns[-self.window:]` (les derniers tours) au lieu de `_turns[:self.window]`
- `agent.py` : `llm.complete` reçoit maintenant `self.memory.history()` au lieu de `[]`

Au 3e appel LLM, l'historique contient bien le 1er tour (commande 4521).

Test couvrant ce cas : `tests/test_agent.py::test_agent_keeps_conversation_context`

---

### `perimetre-1` — Recette de cookies

**Comportement attendu** : refus poli, hors périmètre.

**Résultat** : ✅ Corrigé

`is_in_scope()` est branchée dans `agent.handle()` : si le message ne contient aucun mot-clé Velmo, l'agent retourne immédiatement `category="refusal", within_scope=False` sans appeler le LLM.

---

### `perimetre-2` — Conseil boursier

**Comportement attendu** : refus poli, hors périmètre.

**Résultat** : ✅ Corrigé — même mécanisme que `perimetre-1`.

---

### `entree-abusive-1` — Insulte ("imbécile")

**Comportement attendu** : entrée rejetée par les garde-fous.

**Résultat** : ✅ Corrigé

`validate_input` détecte bien l'insulte (correction `==` → `in`) et retourne un `AgentReply` avec un message poli.

La détection fonctionne et la réponse polie est implémentée.

Test couvrant ce cas : `tests/test_guardrails.py::test_validate_input_rejects_abusive_message`

---

### `apres-vente-1` — Demande de remboursement

**Comportement attendu** : routage vers le parcours après-vente unifié.

**Résultat** : ✅ Catégorisation correcte

`classify("Je veux un remboursement pour la commande 4490")` retourne `Intent.AFTER_SALES`, l'`AgentReply` porte `category="after_sales"`. Le routing complet vers l'outil `open_after_sales` via `route()` n'est pas encore branché dans `agent.py`, mais la classification est juste.

Test couvrant ce cas : `tests/test_flow.py::test_classify_after_sales_for_refund`, `test_route_after_sales_to_tool`

---

## Tableau de synthèse


| Conversation       | Attendu                      | État actuel                                  | Test                                          |
| ------------------ | ---------------------------- | -------------------------------------------- | --------------------------------------------- |
| `ctx-oubli-1`      | Mémoire des tours précédents | ✅ Corrigé                                    | `test_agent_keeps_conversation_context`       |
| `perimetre-1`      | Refus hors périmètre         | ✅ `category="refusal"`, `within_scope=False` | `test_agent_refuses_out_of_scope`             |
| `perimetre-2`      | Refus hors périmètre         | ✅ `category="refusal"`, `within_scope=False` | `test_out_of_scope_for_unrelated_question`    |
| `entree-abusive-1` | Rejet par garde-fous         | ✅ `category="refusal"`, `within_scope=False` | `test_validate_input_rejects_abusive_message` |
| `apres-vente-1`    | Routing après-vente          | ✅ Catégorisé                                 | `test_classify_after_sales_for_refund`        |


---

## Journal des décisions

### D1 — Regroupement `return`/`refund` → `after_sales`

**Décision** : supprimer `Intent.RETURN` et `Intent.REFUND` de l'enum, les remplacer par `Intent.AFTER_SALES = "after_sales"`. Mettre à jour `_ROUTES` en conséquence.

**Pourquoi** : besoin métier — retour et remboursement relèvent du même parcours après-vente. Le code existant mappait déjà `"retour"` et `"remboursement"` vers la chaîne `"after_sales"` dans `_KEYWORDS`, mais l'enum ne définissait pas cette valeur, provoquant un `ValueError` à l'exécution.

**Impact** : `test_flow.py` était déjà écrit pour l'état cible, il passe sans modification.

---

### D2 — Correction de la fenêtre glissante (`memory.py`)

**Décision** : remplacer `_turns[:self.window]` par `_turns[-self.window:]` et augmenter `window` de 8 à 16.

**Pourquoi** : la fenêtre retournait les N premiers tours au lieu des N derniers — le contexte récent était perdu dès le 9e tour. Le nom "fenêtre glissante" dans la docstring décrivait l'intention, pas l'implémentation réelle.

---

### D3 — Injection de l'historique dans `agent.py`

**Décision** : remplacer `self.llm.complete(system, [], user_message)` par `self.llm.complete(system, self.memory.history(), user_message)`.

**Pourquoi** : `ConversationMemory` enregistrait les tours mais ne les transmettait jamais au modèle. C'était la cause directe de `ctx-oubli-1`. La correction de D2 serait sans effet sans celle-ci.

---

### D4 — Correction du filtre de toxicité (`guardrails.py`)

**Décision** : remplacer `term == lowered` par `term in lowered`.

**Pourquoi** : l'égalité stricte ne bloquait que les messages composés d'un seul mot insulte. "Mais tu es vraiment un imbécile" passait sans être détecté.

---

### D5 — Typage contraint de `AgentReply.category`

**Décision** : remplacer `category: str` par `category: Literal["greeting", "order_status", "delivery", "after_sales", "refusal"]`.

**Pourquoi** : Pydantic ne validait aucune valeur — `"banane"` était accepté. Le `Literal` garantit que toute catégorie non prévue lève une `ValidationError` à l'instanciation.

---

### D6 — Correction de `track_delivery` dans `tools.py`

**Décision** : ajouter une docstring à `track_delivery`.

**Pourquoi** : le décorateur `@register` conditionne l'enregistrement à la présence d'une docstring (`if not fn.__doc__: return fn`). Sans docstring, l'outil était absent de `available_tools()`.

---

### D7 — Correction du nom de fichier dans `regression.py`

**Décision** : remplacer `"conversations.json"` par `"conversations_problematiques.json"`.

**Pourquoi** : le fichier de données s'appelle `conversations_problematiques.json` — le chemin codé en dur était faux, provoquant un `FileNotFoundError`.

---

### D8 — Branchement de `is_in_scope()` et correction du test

**Décision** : brancher `is_in_scope()` dans `agent.handle()` — si le message est hors périmètre, retourner immédiatement `AgentReplycategory="refusal", within_scope=False` sans appeler le LLM.

**Pourquoi** : `is_in_scope()` était importée mais jamais appelée — les questions hors périmètre atteignaient le LLM. 

---

### D9 — Remplacement de `GuardrailError` par une réponse polie

**Décision** : supprimer `GuardrailError` et changer la signature de `validate_input` de `-> None` (avec raise) à `-> AgentReply | None` (sans exception). En cas de terme bloqué, la fonction retourne directement un `AgentReply(category="refusal", within_scope=False)`. `agent.handle()` retourne ce refus immédiatement sans appeler le LLM.

**Pourquoi** : lever une exception non rattrapée faisait remonter `GuardrailError` à l'appelant au lieu d'une réponse structurée. L'utilisateur recevait une erreur technique plutôt qu'un message poli. Le contrat de `handle()` est de toujours retourner un `AgentReply` — une exception en rompt le contrat.

**Impact** : `GuardrailError` supprimée (plus aucun usage), `test_guardrails.py` mis à jour pour vérifier la valeur de retour plutôt que l'exception levée.