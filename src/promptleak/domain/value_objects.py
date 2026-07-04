import re
from dataclasses import dataclass
from enum import Enum, IntEnum

_GRADE_THRESHOLDS = (
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (50, "E"),
)


class Severity(IntEnum):
    """Gravité d'un Finding, ordonnée du moins au plus grave."""

    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @property
    def score_penalty(self) -> int:
        return {
            Severity.INFO: 0,
            Severity.LOW: 3,
            Severity.MEDIUM: 10,
            Severity.HIGH: 25,
            Severity.CRITICAL: 40,
        }[self]


class InjectionVector(Enum):
    """Où une tentative d'injection a été testée."""

    STATIC_DESCRIPTION = "static_description"
    DYNAMIC_RESPONSE = "dynamic_response"


@dataclass(frozen=True)
class McpTargetConfig:
    """Décrit comment lancer/atteindre un serveur MCP cible (transport stdio)."""

    name: str
    command: str
    args: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("McpTargetConfig name must not be empty")
        if not self.command.strip():
            raise ValueError("McpTargetConfig command must not be empty")


@dataclass(frozen=True)
class Scenario:
    """Une tâche légitime donnée à l'agent de test dynamique."""

    id: str
    user_task: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Scenario id must not be empty")
        if not self.user_task.strip():
            raise ValueError("Scenario user_task must not be empty")


@dataclass(frozen=True)
class Evidence:
    """Extrait de texte ou de transcript justifiant un Finding."""

    excerpt: str

    def __post_init__(self) -> None:
        if not self.excerpt.strip():
            raise ValueError("Evidence excerpt must not be empty")


@dataclass(frozen=True)
class InjectionPattern:
    """Une technique connue d'injection, cherchée dans le texte d'un McpTool."""

    technique: str
    severity: Severity
    regex: str
    explanation: str

    def __post_init__(self) -> None:
        if not self.technique.strip():
            raise ValueError("InjectionPattern technique must not be empty")
        if not self.explanation.strip():
            raise ValueError("InjectionPattern explanation must not be empty")
        try:
            re.compile(self.regex)
        except re.error as error:
            raise ValueError(f"InjectionPattern regex is invalid: {self.regex!r}") from error


@dataclass(frozen=True)
class Score:
    """Score agrégé 0-100 d'un scan, avec sa note dérivée."""

    value: int

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 100:
            raise ValueError(f"Score must be between 0 and 100, got {self.value}")

    @property
    def grade(self) -> str:
        for threshold, letter in _GRADE_THRESHOLDS:
            if self.value >= threshold:
                return letter
        return "F"
