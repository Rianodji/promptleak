# promptleak

Scanner d'injection de prompt pour serveurs MCP (Model Context Protocol) —
détecte le *tool poisoning* statique (descriptions d'outils) et dynamique
(réponses d'outils qui détournent un agent) sur des serveurs MCP, avec un
score de risque agrégé.

Voir [SCOPE.md](SCOPE.md) pour le périmètre v1, [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
pour la conception (hexagonale/DDD), [docs/PAYLOADS.md](docs/PAYLOADS.md)
pour la bibliothèque de techniques d'injection détectées, et
[ROADMAP.md](ROADMAP.md) pour les pistes d'amélioration futures.

## ⚠️ Avertissement

À utiliser **uniquement** sur des serveurs MCP dont vous êtes propriétaire ou
pour lesquels vous avez une autorisation explicite. Le mode dynamique fait
tourner un vrai agent LLM contre la cible et effectue des appels API réels et
facturés (API Anthropic).

## Installation

```bash
git clone git@github.com:Rianodji/promptleak.git
cd promptleak
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Pour le mode dynamique, une clé API Anthropic est nécessaire :

```bash
cp .env.example .env
# puis éditer .env et renseigner ANTHROPIC_API_KEY
```

## Usage

### Scan statique (gratuit, aucune I/O externe hors la cible)

Analyse les descriptions d'outils exposées par un serveur MCP, sans les
exécuter ni faire appel à un LLM :

```bash
promptleak python3 mon_serveur_mcp.py
```

`COMMAND` et ses arguments décrivent comment lancer le serveur MCP cible
(transport stdio). Le nom affiché dans le rapport peut être personnalisé :

```bash
promptleak python3 mon_serveur_mcp.py --name "mon-serveur"
```

### Scan dynamique (fait de vrais appels API facturés)

Ajoute un ou plusieurs `--dynamic-task` : chacun devient un scénario confié à
un agent Claude réel, branché sur le serveur cible, pour observer s'il se
fait détourner par une réponse d'outil piégée :

```bash
promptleak python3 mon_serveur_mcp.py \
  --dynamic-task "Utilise l'outil read_notes pour résumer mes notes." \
  --dynamic-task "Utilise l'outil search_docs pour trouver le contrat X."
```

### Essayer sur les serveurs de lab fournis

Le dépôt inclut des serveurs MCP factices dans `labs/`, utilisés aussi comme
cibles de test automatisé :

```bash
# Cible propre : score attendu 100/100
promptleak python3 labs/clean_server.py

# Cible avec injection statique volontaire : score attendu 0/100
promptleak python3 labs/poisoned_description_server.py

# Cible avec injection dynamique volontaire (réponse d'outil piégée)
promptleak python3 labs/poisoned_response_server.py \
  --dynamic-task "Utilise read_notes sur 'perso.txt' et fais-moi un résumé."
```

## Comment lire le rapport

- **Score** (0–100) et **note** (A–F) : plus c'est élevé, moins la cible
  semble vulnérable. Voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#4-modèle-de-domaine-ddd)
  pour le détail du calcul.
- **Findings** : chaque ligne indique l'outil concerné, le vecteur
  (`static_description` ou `dynamic_response`), la technique détectée, sa
  sévérité, et un extrait de preuve.
- Un score de 100 sans finding ne prouve pas l'absence totale de risque : il
  signifie que la bibliothèque de patterns actuelle (voir
  [docs/PAYLOADS.md](docs/PAYLOADS.md)) et les scénarios dynamiques testés
  n'ont rien détecté.

## Limites connues (v1)

- Ne teste que des serveurs MCP en transport stdio (pas SSE/HTTP).
- Le mode dynamique dépend du comportement du modèle testé : un résultat
  "propre" peut refléter la résistance du modèle à l'injection testée, pas
  l'absence de piège dans le serveur.
- Bibliothèque de patterns statiques volontairement restreinte en v1 (voir
  [docs/PAYLOADS.md](docs/PAYLOADS.md)) — à enrichir en itération (phase 8).

## Développement

```bash
pytest
ruff check .
mypy src
```

Les tests qui appellent réellement l'API Anthropic sont automatiquement
ignorés si `ANTHROPIC_API_KEY` n'est pas définie (utile en CI).
