import secrets

from promptleak.domain.entities import ScanReport
from promptleak.domain.ports.mcp_server_port import McpServerPort
from promptleak.domain.ports.payload_repository_port import PayloadRepositoryPort
from promptleak.domain.ports.test_agent_port import TestAgentPort
from promptleak.domain.services.dynamic_analysis_service import DynamicAnalysisService
from promptleak.domain.services.scoring_service import ScoringService
from promptleak.domain.services.static_analysis_service import StaticAnalysisService
from promptleak.domain.value_objects import McpTargetConfig, Scenario, Score


class ScanServerUseCase:
    """Orchestre un scan complet (statique, et dynamique si des Scenario sont
    fournis) sur une Target, et retourne le ScanReport ainsi que son Score."""

    def __init__(
        self,
        mcp_server_port: McpServerPort,
        payload_repository_port: PayloadRepositoryPort,
        test_agent_port: TestAgentPort | None = None,
        static_analysis_service: StaticAnalysisService | None = None,
        dynamic_analysis_service: DynamicAnalysisService | None = None,
        scoring_service: ScoringService | None = None,
    ) -> None:
        self._mcp_server_port = mcp_server_port
        self._payload_repository_port = payload_repository_port
        self._test_agent_port = test_agent_port
        self._static_analysis_service = static_analysis_service or StaticAnalysisService()
        self._dynamic_analysis_service = dynamic_analysis_service or DynamicAnalysisService()
        self._scoring_service = scoring_service or ScoringService()

    async def execute(
        self, target: McpTargetConfig, scenarios: list[Scenario] | None = None
    ) -> tuple[ScanReport, Score]:
        scenarios = scenarios or []
        report = ScanReport(target_name=target.name)

        tools = await self._mcp_server_port.list_tools(target)
        patterns = self._payload_repository_port.load_static_patterns()
        for finding in self._static_analysis_service.analyze(tools, patterns):
            report.add_finding(finding)

        if scenarios and self._test_agent_port is not None:
            canary = f"CANARY-{secrets.token_hex(8)}"
            for scenario in scenarios:
                transcript = await self._test_agent_port.run_scenario(target, scenario, canary)
                for finding in self._dynamic_analysis_service.analyze(transcript, canary):
                    report.add_finding(finding)

        score = report.compute_score(self._scoring_service)
        return report, score
