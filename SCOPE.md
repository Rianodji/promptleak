# promptleak — Cadrage (v1)

## Objectif

Détecter automatiquement si un serveur MCP (Model Context Protocol) est vulnérable
à l'injection de prompt, via deux angles :

1. **Injection statique** : instructions cachées dans les *descriptions* des outils
   MCP exposés par le serveur (le serveur peut manipuler un agent avant même qu'un
   outil soit appelé, juste via le texte de sa définition).
2. **Injection dynamique** : instructions cachées dans les *données retournées*
   par un outil, testées en conditions réelles avec un agent qui utilise le serveur.

## Cible v1

Des serveurs MCP **factices, créés par nous**, dans un lab contrôlé. Pas de serveurs
tiers/publics en v1 — objectif d'apprentissage et de sécurité (on ne teste que ce
qu'on possède).

## Fonctionnalités v1 (in scope)

- **Moteur d'analyse statique** : récupère la liste des outils d'un serveur MCP
  (nom, description, schéma des paramètres) et la scanne avec une bibliothèque de
  patterns/payloads d'injection connus (instructions impératives cachées, faux tags
  système, encodage suspect, etc.).
- **Moteur d'analyse dynamique** : fait tourner un agent réel (API Anthropic) contre
  le serveur MCP cible, avec des scénarios de tâches légitimes, et observe si les
  réponses des outils parviennent à faire dévier l'agent de sa tâche (fuite de
  system prompt, exécution d'une action non demandée, etc.).
- **Système de scoring** :
  - Sévérité par test individuel : `info / low / medium / high / critical`, selon
    l'impact observé (simple déviation de réponse → fuite de données → action
    non autorisée réellement déclenchée).
  - Score agrégé par serveur testé (0–100 ou note A–F), calculé à partir des
    sévérités des tests individuels.
- **CLI** : commande pour lancer un scan sur un serveur MCP cible (config de
  connexion en argument/fichier) et afficher un rapport (liste des outils testés,
  payloads qui ont réussi, score final).
- **Bibliothèque de serveurs MCP de lab** : quelques serveurs MCP jouets qu'on
  développe nous-mêmes, avec des vulnérabilités volontairement injectées, pour
  valider que le scanner les détecte bien (cibles de test/CI).

## Hors scope v1 (remis à plus tard)

- Scanner des serveurs MCP tiers/publics réels.
- Support d'autres backends LLM que l'API Anthropic pour le mode dynamique
  (architecture pensée pour rester découplée, mais pas implémenté en v1).
- Interface web / dashboard (CLI uniquement en v1).
- Détection de l'injection via RAG/documents externes (hors périmètre MCP).
- Intégration CI/CD packagée pour des tiers (pip install propre, etc.) — viendra
  en phase de publication.

## Choix techniques

- **Agent de test dynamique** : API Anthropic (Claude), via le SDK officiel.
- Langage et structure détaillée : à trancher en phase 2 (recherche & conception).

## Éthique & légal

Outil destiné exclusivement à tester des serveurs MCP dont on est propriétaire ou
pour lesquels on a une autorisation explicite. Un disclaimer sera inclus dans le
README (phase documentation).
