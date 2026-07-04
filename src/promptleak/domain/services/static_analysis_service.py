import re

from promptleak.domain.entities import Finding, McpTool
from promptleak.domain.value_objects import Evidence, InjectionPattern, InjectionVector


def _texts_to_scan(tool: McpTool) -> list[str]:
    texts = [tool.description]
    properties = tool.input_schema.get("properties", {})
    if isinstance(properties, dict):
        for parameter_schema in properties.values():
            if isinstance(parameter_schema, dict):
                description = parameter_schema.get("description")
                if isinstance(description, str):
                    texts.append(description)
    return [text for text in texts if text]


class StaticAnalysisService:
    """Scanne les métadonnées (description, paramètres) des McpTool à la recherche
    de patterns d'injection connus — aucune exécution, aucune I/O."""

    def analyze(
        self, tools: list[McpTool], patterns: list[InjectionPattern]
    ) -> list[Finding]:
        findings: list[Finding] = []
        for tool in tools:
            for text in _texts_to_scan(tool):
                for pattern in patterns:
                    match = re.search(pattern.regex, text)
                    if match:
                        findings.append(
                            Finding(
                                tool_name=tool.name,
                                vector=InjectionVector.STATIC_DESCRIPTION,
                                technique=pattern.technique,
                                severity=pattern.severity,
                                evidence=Evidence(excerpt=match.group(0)),
                                explanation=pattern.explanation,
                            )
                        )
        return findings
