from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from promptleak.domain.value_objects import Evidence, InjectionVector, Score, Severity

if TYPE_CHECKING:
    from promptleak.domain.services.scoring_service import ScoringService


@dataclass(frozen=True)
class McpTool:
    """Un outil exposé par un serveur MCP cible."""

    name: str
    description: str
    input_schema: dict

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("McpTool name must not be empty")


@dataclass(frozen=True)
class ToolCallRecord:
    """Un appel d'outil observé pendant l'exécution d'un Scenario par l'agent."""

    tool_name: str
    arguments: dict


@dataclass(frozen=True)
class AgentTranscript:
    """Ce qui s'est passé quand l'agent de test a exécuté un Scenario contre une Target."""

    scenario_id: str
    final_answer: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)


@dataclass(frozen=True)
class Finding:
    """Le résultat d'un test d'injection sur un outil donné."""

    tool_name: str
    vector: InjectionVector
    technique: str
    severity: Severity
    evidence: Evidence
    explanation: str

    def __post_init__(self) -> None:
        if not self.technique.strip():
            raise ValueError("Finding technique must not be empty")


@dataclass
class ScanReport:
    """Agrégat racine : tous les Findings d'un scan sur une Target."""

    target_name: str
    findings: list[Finding] = field(default_factory=list)

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)

    def findings_by_severity(self, severity: Severity) -> list[Finding]:
        return [f for f in self.findings if f.severity == severity]

    def is_vulnerable(self) -> bool:
        return len(self.findings) > 0

    def compute_score(self, scoring_service: "ScoringService") -> Score:
        return scoring_service.compute(self.findings)
