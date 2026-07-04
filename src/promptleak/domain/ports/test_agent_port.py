from abc import ABC, abstractmethod

from promptleak.domain.entities import AgentTranscript
from promptleak.domain.value_objects import McpTargetConfig, Scenario


class TestAgentPort(ABC):
    """Port : fait exécuter un Scenario par un agent réel contre une Target,
    et retourne ce qui s'est passé (réponse finale, appels d'outils)."""

    @abstractmethod
    async def run_scenario(
        self, target: McpTargetConfig, scenario: Scenario, canary: str
    ) -> AgentTranscript: ...
