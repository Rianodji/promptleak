from click.testing import CliRunner

import promptleak.interface.cli.cli as cli_module
from promptleak.domain.entities import ScanReport
from promptleak.domain.value_objects import Score


class FakeUseCase:
    def __init__(self, report: ScanReport, score: Score) -> None:
        self._report = report
        self._score = score
        self.received_target = None
        self.received_scenarios = None

    async def execute(self, target, scenarios):
        self.received_target = target
        self.received_scenarios = scenarios
        return self._report, self._score


def test_scan_command_reports_a_clean_target(monkeypatch):
    fake_use_case = FakeUseCase(ScanReport(target_name="clean-lab"), Score(value=100))
    monkeypatch.setattr(
        cli_module, "build_scan_use_case", lambda with_dynamic_agent: fake_use_case
    )

    result = CliRunner().invoke(
        cli_module.scan, ["python3", "server.py", "--name", "clean-lab"]
    )

    assert result.exit_code == 0
    assert "clean-lab" in result.output
    assert "100/100" in result.output
    assert fake_use_case.received_target.command == "python3"
    assert fake_use_case.received_target.args == ("server.py",)
    assert fake_use_case.received_scenarios == []


def test_scan_command_defaults_the_target_name_to_the_command(monkeypatch):
    fake_use_case = FakeUseCase(ScanReport(target_name="ignored"), Score(value=100))
    monkeypatch.setattr(
        cli_module, "build_scan_use_case", lambda with_dynamic_agent: fake_use_case
    )

    result = CliRunner().invoke(cli_module.scan, ["python3", "server.py"])

    assert result.exit_code == 0
    assert fake_use_case.received_target.name == "python3"


def test_scan_command_builds_one_scenario_per_dynamic_task_option(monkeypatch):
    fake_use_case = FakeUseCase(ScanReport(target_name="lab"), Score(value=100))
    with_dynamic_agent_calls = []
    monkeypatch.setattr(
        cli_module,
        "build_scan_use_case",
        lambda with_dynamic_agent: with_dynamic_agent_calls.append(with_dynamic_agent)
        or fake_use_case,
    )

    result = CliRunner().invoke(
        cli_module.scan,
        ["python3", "server.py", "--dynamic-task", "Fais X", "--dynamic-task", "Fais Y"],
    )

    assert result.exit_code == 0
    assert with_dynamic_agent_calls == [True]
    assert [s.user_task for s in fake_use_case.received_scenarios] == ["Fais X", "Fais Y"]
