import pytest

from promptleak.domain.value_objects import Evidence, Score, Severity


def test_severity_is_ordered_from_info_to_critical():
    assert Severity.INFO < Severity.LOW < Severity.MEDIUM < Severity.HIGH < Severity.CRITICAL


@pytest.mark.parametrize(
    "severity,expected_penalty",
    [
        (Severity.INFO, 0),
        (Severity.LOW, 3),
        (Severity.MEDIUM, 10),
        (Severity.HIGH, 25),
        (Severity.CRITICAL, 40),
    ],
)
def test_severity_score_penalty(severity, expected_penalty):
    assert severity.score_penalty == expected_penalty


def test_evidence_rejects_empty_excerpt():
    with pytest.raises(ValueError):
        Evidence(excerpt="   ")


@pytest.mark.parametrize(
    "value,expected_grade",
    [
        (100, "A"),
        (90, "A"),
        (85, "B"),
        (72, "C"),
        (61, "D"),
        (55, "E"),
        (10, "F"),
        (0, "F"),
    ],
)
def test_score_grade_thresholds(value, expected_grade):
    assert Score(value=value).grade == expected_grade


@pytest.mark.parametrize("invalid_value", [-1, 101, 1000])
def test_score_rejects_out_of_range_values(invalid_value):
    with pytest.raises(ValueError):
        Score(value=invalid_value)
