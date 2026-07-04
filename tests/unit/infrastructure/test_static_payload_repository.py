from promptleak.domain.value_objects import Severity
from promptleak.infrastructure.adapters.payloads.static_payload_repository import (
    StaticPayloadRepository,
)


def test_loads_the_bundled_payload_library():
    patterns = StaticPayloadRepository().load_static_patterns()

    assert len(patterns) >= 5
    techniques = {p.technique for p in patterns}
    assert "impersonated_system_instruction" in techniques
    assert "exfiltration_request" in techniques

    critical = next(p for p in patterns if p.technique == "exfiltration_request")
    assert critical.severity == Severity.CRITICAL
