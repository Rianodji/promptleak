from importlib import resources
from pathlib import Path

import yaml

from promptleak.domain.ports.payload_repository_port import PayloadRepositoryPort
from promptleak.domain.value_objects import InjectionPattern, Severity

_DEFAULT_PAYLOADS_FILE = resources.files("promptleak.infrastructure.adapters.payloads").joinpath(
    "payloads.yaml"
)


class StaticPayloadRepository(PayloadRepositoryPort):
    """Charge la bibliothèque de patterns d'injection depuis un fichier YAML."""

    def __init__(self, payloads_file: Path | None = None) -> None:
        self._payloads_file = payloads_file or _DEFAULT_PAYLOADS_FILE

    def load_static_patterns(self) -> list[InjectionPattern]:
        raw = yaml.safe_load(self._payloads_file.read_text(encoding="utf-8"))
        return [
            InjectionPattern(
                technique=entry["technique"],
                severity=Severity[entry["severity"].upper()],
                regex=entry["regex"],
                explanation=entry["explanation"].strip(),
            )
            for entry in raw["patterns"]
        ]
