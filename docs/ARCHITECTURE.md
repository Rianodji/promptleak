# promptleak — Conception & Architecture

## 1. Principes retenus

- **Architecture hexagonale (ports & adaptateurs)** : le domaine métier ne connaît
  rien du monde extérieur (SDK MCP, API Anthropic, CLI). Il définit des
  **ports** (interfaces) que l'infrastructure vient implémenter via des
  **adaptateurs**. La dépendance va toujours de l'extérieur vers le centre,
  jamais l'inverse.
- **Clean Architecture** : quatre cercles — Domain (cœur métier) → Application
  (cas d'usage) → Infrastructure (adaptateurs techniques) → Interface (CLI).
  Le code du centre ne dépend jamais du code des cercles extérieurs.
- **DDD (Domain-Driven Design)** : on modélise le métier avec un langage
  ubiquitaire (glossaire ci-dessous), des entités, des value objects, un
  agrégat racine, et des services de domaine pour la logique qui n'appartient
  pas naturellement à un objet.
- **Clean Code** : fonctions courtes à une responsabilité, noms explicites,
  pas de logique métier dans les adaptateurs ni dans la CLI.

## 2. Langage ubiquitaire (glossaire du domaine)

| Terme | Définition |
|---|---|
| **Target** | Le serveur MCP qu'on scanne. |
| **McpTool** | Un outil exposé par une Target (nom, description, schéma des paramètres). |
| **InjectionVector** | Où l'injection a été testée : `STATIC_DESCRIPTION` (métadonnées de l'outil) ou `DYNAMIC_RESPONSE` (réponse de l'outil à l'exécution). |
| **InjectionPattern / Payload** | Une technique connue de tentative d'injection, utilisée pour tester une Target. |
| **Finding** | Un résultat de test : une technique testée sur un outil donné, avec son verdict et sa sévérité. |
| **Severity** | Gravité d'un Finding : `INFO / LOW / MEDIUM / HIGH / CRITICAL`. |
| **ScanReport** | Agrégat racine : l'ensemble des Findings d'un scan sur une Target, avec un Score calculé. |
| **Score / Grade** | Note agrégée (0–100 / A–F) résumant le niveau de risque d'une Target. |
| **Scenario** | Une tâche légitime donnée à l'agent de test dynamique pour observer son comportement face à une Target. |

## 3. Vue hexagonale

```
                         ┌───────────────────────────────┐
                         │      Interface (driving)       │
                         │           cli.py               │
                         └───────────────┬─────────────────┘
                                         │ appelle
                         ┌───────────────▼─────────────────┐
                         │       Application (use cases)    │
                         │      ScanServerUseCase           │
                         └───┬───────────────────────┬─────┘
                             │ utilise (ports)        │
              ┌──────────────▼───────────┐   ┌────────▼──────────────┐
              │           DOMAIN          │   │   DOMAIN (ports)       │
              │  Entities / Value Objects │   │  McpServerPort         │
              │  Finding, ScanReport,     │   │  TestAgentPort         │
              │  Severity, Score          │   │  PayloadRepositoryPort │
              │  Services: StaticAnalysis,│   └────────┬──────────────┘
              │  ScoringService           │            │ implémentés par
              └───────────────────────────┘   ┌────────▼──────────────┐
                                               │  Infrastructure         │
                                               │  (driven adapters)      │
                                               │  McpSdkServerAdapter    │
                                               │  AnthropicTestAgent     │
                                               │  StaticPayloadRepo      │
                                               └─────────────────────────┘
```

Règle de dépendance : `interface → application → domain ← infrastructure`.
Le domaine ne dépend de rien ; tout le reste dépend du domaine (via les ports).

## 4. Modèle de domaine (DDD)

### Value Objects (immuables, pas d'identité)
- `Severity` : enum ordonné `INFO < LOW < MEDIUM < HIGH < CRITICAL`, porte le
  poids utilisé pour le scoring.
- `InjectionVector` : enum `STATIC_DESCRIPTION | DYNAMIC_RESPONSE`.
- `Score` : entier 0–100 + `Grade` (A–F) dérivé.
- `Evidence` : extrait de texte / transcript justifiant un Finding.

### Entités
- `McpTool` : identifié par son nom, porte description + schéma de paramètres.
- `Finding` : identifié par (outil, vecteur, technique) — sévérité, preuve,
  description humaine du problème.

### Agrégat racine
- `ScanReport` : regroupe tous les `Finding` d'un scan sur une `Target`, expose
  `compute_score()` en délégant au `ScoringService`. C'est le seul objet que
  l'application manipule en sortie d'un scan — on ne modifie jamais un
  `Finding` isolément depuis l'extérieur de l'agrégat.

### Services de domaine (logique pure, sans I/O)
- `StaticAnalysisService.analyze(tools: list[McpTool], patterns: list[InjectionPattern]) -> list[Finding]`
- `ScoringService.compute(findings: list[Finding]) -> Score`

Ces services sont 100% testables sans mock, sans réseau, sans SDK.

## 5. Ports (interfaces définies par le domaine)

- `McpServerPort` : `list_tools(target) -> list[McpTool]`
- `TestAgentPort` : `run_scenarios(target, scenarios) -> list[Transcript]`
  (fait tourner l'agent Claude branché sur le serveur MCP cible et retourne ce
  qui s'est passé, pour analyse par un `DynamicAnalysisService` à venir)
- `PayloadRepositoryPort` : `load_static_patterns() -> list[InjectionPattern]`

## 6. Application — cas d'usage

- `ScanServerUseCase.execute(target_config, mode) -> ScanReport`
  1. Récupère les outils via `McpServerPort`.
  2. Charge les patterns via `PayloadRepositoryPort`.
  3. Lance `StaticAnalysisService` → Findings statiques.
  4. Si mode dynamique : lance les scénarios via `TestAgentPort`, analyse les
     transcripts → Findings dynamiques.
  5. Construit le `ScanReport` (agrégat), calcule le score.
  6. Retourne le rapport à l'appelant (CLI).

L'use case orchestre ; il ne contient aucune règle métier lui-même (elle vit
dans les services de domaine).

## 7. Infrastructure — adaptateurs (implémentent les ports)

- `McpSdkServerAdapter` : implémente `McpServerPort` avec le SDK officiel `mcp`.
- `AnthropicTestAgentAdapter` : implémente `TestAgentPort` avec le SDK `anthropic`
  + le client MCP, pour faire tourner un vrai agent contre la Target.
- `StaticPayloadRepository` : implémente `PayloadRepositoryPort`, charge les
  patterns depuis un fichier `payloads.yaml` versionné avec le code.

## 8. Interface — adaptateur pilote (driving)

- `cli.py` : parse les arguments, construit l'`use case` (composition root dans
  `bootstrap.py`), l'exécute, passe le `ScanReport` à un `ReportPresenter`
  (rendu `rich` dans le terminal).

## 9. Structure de dossiers

```
promptleak/
  src/promptleak/
    domain/
      entities.py
      value_objects.py
      services/
        static_analysis_service.py
        scoring_service.py
      ports/
        mcp_server_port.py
        test_agent_port.py
        payload_repository_port.py
    application/
      use_cases/
        scan_server_use_case.py
    infrastructure/
      adapters/
        mcp/mcp_sdk_server_adapter.py
        agent/anthropic_test_agent_adapter.py
        payloads/static_payload_repository.py
        payloads/payloads.yaml
    interface/
      cli/
        cli.py
        presenter.py
    bootstrap.py          # composition root : câble les ports aux adaptateurs
  labs/                    # serveurs MCP factices, cibles de test
    clean_server.py
    poisoned_description_server.py
    poisoned_response_server.py
  tests/
    unit/domain/           # tests du cœur métier, sans I/O
    integration/            # tests des adaptateurs contre les labs
  docs/
    ARCHITECTURE.md         # ce fichier
  SCOPE.md
```

## 10. Pourquoi ce découpage

- Le **domaine testable sans I/O** (`StaticAnalysisService`, `ScoringService`)
  permet d'écrire des tests unitaires rapides et fiables dès la phase 4.
- Remplacer l'API Anthropic par un autre modèle plus tard = un seul nouvel
  adaptateur à écrire (`OtherLlmTestAgentAdapter`), zéro changement dans le
  domaine ou l'application.
- Ajouter un nouveau vecteur d'injection (ex: RAG) plus tard = un nouveau port
  + adaptateur, sans toucher au `ScoringService` ni au `ScanReport`.
