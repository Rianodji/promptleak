from abc import ABC, abstractmethod

from promptleak.domain.value_objects import InjectionPattern


class PayloadRepositoryPort(ABC):
    """Port : fournit la bibliothèque de patterns d'injection connus."""

    @abstractmethod
    def load_static_patterns(self) -> list[InjectionPattern]: ...
