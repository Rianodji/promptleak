# Bibliothèque de patterns d'injection

Ce document décrit les techniques recherchées par `StaticAnalysisService`, dont
la source de vérité est
[`payloads.yaml`](../src/promptleak/infrastructure/adapters/payloads/payloads.yaml).
Chaque pattern est un objet `InjectionPattern` (technique, sévérité, regex,
explication), chargé au démarrage par `StaticPayloadRepository`.

Le scan statique applique chaque pattern au texte de la `description` de
chaque outil MCP, ainsi qu'aux descriptions de ses paramètres
(`inputSchema.properties.*.description`).

| Technique | Sévérité | Ce qu'elle détecte |
|---|---|---|
| `impersonated_system_instruction` | HIGH | Une instruction du type « ignore les instructions précédentes », visant à faire perdre à l'agent le contexte de ses consignes légitimes. |
| `exfiltration_request` | CRITICAL | Une demande d'envoyer/transférer une copie de données vers une adresse tierce (`send/forward/cc/bcc ... to <email>`) — tentative d'exfiltration directe. |
| `hidden_role_tag` | HIGH | Une balise imitant un rôle de confiance (`<system>`, `<assistant>`) dans une simple métadonnée d'outil, pour se faire passer pour une instruction du système plutôt qu'une description. |
| `fake_urgency_directive` | MEDIUM | Un ton impératif inhabituel dans une description d'outil (« IMPORTANT... always/never/before... ») typique des tentatives de manipulation d'agent. |
| `suspicious_encoded_blob` | LOW | Un bloc de texte encodé (probablement base64) susceptible de cacher des instructions non lisibles directement. |

## Pourquoi ces sévérités

Le poids retenu par `Severity.score_penalty` (voir
[docs/ARCHITECTURE.md](ARCHITECTURE.md)) reflète l'impact potentiel si
l'agent suit l'instruction cachée :
- **CRITICAL** (`exfiltration_request`) : fuite de données vers un tiers —
  impact direct et concret.
- **HIGH** (`impersonated_system_instruction`, `hidden_role_tag`) : perte de
  contrôle du comportement de l'agent, mais sans preuve d'impact concret par
  la seule analyse statique.
- **MEDIUM** (`fake_urgency_directive`) : signal suspect mais plus
  ambigu — peut aussi être un simple style d'écriture maladroit (faux
  positif possible).
- **LOW** (`suspicious_encoded_blob`) : signal faible, un blob encodé peut
  être légitime (ex : un exemple de token dans la doc d'un paramètre).

## Limites

- Détection par expression régulière uniquement : contournable par
  reformulation, encodage non couvert, ou une langue non anglaise/française.
- Aucune analyse sémantique : un texte qui évoque ces motifs sans être une
  vraie tentative d'injection peut déclencher un faux positif (notamment
  `fake_urgency_directive` et `suspicious_encoded_blob`).
- Bibliothèque volontairement restreinte pour la v1 — l'enrichissement (plus
  de techniques, détection multilingue, contournements d'encodage) est prévu
  en phase 8 (itération).

## Ajouter un nouveau pattern

Éditer `payloads.yaml` et ajouter une entrée :

```yaml
- technique: nom_de_la_technique
  severity: low|medium|high|critical
  regex: "(?i)votre expression régulière"
  explanation: >
    Explication humaine de ce que ce pattern détecte et pourquoi c'est
    suspect.
```

Aucun changement de code n'est nécessaire — `StaticPayloadRepository` charge
le fichier dynamiquement. Ajouter aussi un cas de test dans
`labs/poisoned_description_server.py` et son assertion correspondante dans
`tests/integration/test_static_scan_end_to_end.py` pour valider la détection
de bout en bout.
