# Roadmap — pistes d'amélioration (phase 8 : itération)

La v1 (voir [SCOPE.md](SCOPE.md)) est fonctionnelle de bout en bout. Ce
fichier liste les pistes identifiées pour la suite, à reprendre au fil du
temps — aucune urgence, aucun ordre imposé.

## Détection statique

- Enrichir `payloads.yaml` : plus de techniques, détection multilingue
  (les patterns actuels sont surtout en anglais), contournements d'encodage
  (unicode, homoglyphes, autres que base64).
- Passer d'une détection par regex à une détection sémantique (ex : faire
  juger le texte par un LLM) pour réduire les faux positifs/négatifs des
  patterns actuels — voir les limites listées dans
  [docs/PAYLOADS.md](docs/PAYLOADS.md).
- Détection du **rug pull** : garder un historique des descriptions d'un
  serveur MCP déjà scanné et alerter si elles changent entre deux scans.

## Détection dynamique

- Ajouter des scénarios/techniques au-delà de la fuite de canari : appel
  d'un outil non autorisé par la tâche demandée, contournement de garde-fou,
  fuite du system prompt complet (pas juste le canari).
- Rendre les réponses piégées de `labs/poisoned_response_server.py` plus
  variées, pour couvrir plusieurs styles d'injection dynamique.
- Support d'un autre backend LLM que l'API Anthropic pour l'agent de test
  (l'architecture le permet déjà : un nouvel adaptateur `TestAgentPort`
  suffit, voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)).

## Cibles

- Support d'autres transports MCP (SSE / HTTP), au-delà du stdio actuel.
- Lever la limite « labs seulement » pour scanner de vrais serveurs MCP
  tiers/publics (avec autorisation), une fois le scanner mûr.

## Distribution & outillage

- Packaging propre pour publication (PyPI ou équivalent).
- Interface web / dashboard en plus de la CLI actuelle.

## Hors scope pour l'instant

- Détection d'injection via RAG/documents externes (hors périmètre MCP).
