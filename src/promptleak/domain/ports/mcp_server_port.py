from abc import ABC, abstractmethod

from promptleak.domain.entities import McpTool
from promptleak.domain.value_objects import McpTargetConfig


class McpServerPort(ABC):
    """Port : liste les outils exposés par un serveur MCP cible."""

    @abstractmethod
    async def list_tools(self, target: McpTargetConfig) -> list[McpTool]: ...
