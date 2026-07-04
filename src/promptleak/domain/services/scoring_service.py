from promptleak.domain.entities import Finding
from promptleak.domain.value_objects import Score

_MAX_SCORE = 100
_MIN_SCORE = 0


class ScoringService:
    """Calcule le Score agrégé d'un scan à partir de ses Findings."""

    def compute(self, findings: list[Finding]) -> Score:
        total_penalty = sum(finding.severity.score_penalty for finding in findings)
        value = max(_MIN_SCORE, _MAX_SCORE - total_penalty)
        return Score(value=value)
