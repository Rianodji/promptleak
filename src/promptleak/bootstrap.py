from dotenv import load_dotenv

from promptleak.application.use_cases.scan_server_use_case import ScanServerUseCase
from promptleak.infrastructure.adapters.agent.anthropic_test_agent_adapter import (
    AnthropicTestAgentAdapter,
)
from promptleak.infrastructure.adapters.mcp.mcp_sdk_server_adapter import McpSdkServerAdapter
from promptleak.infrastructure.adapters.payloads.static_payload_repository import (
    StaticPayloadRepository,
)


def build_scan_use_case(with_dynamic_agent: bool) -> ScanServerUseCase:
    """Composition root : câble les ports du domaine à leurs adaptateurs réels."""
    load_dotenv()
    return ScanServerUseCase(
        mcp_server_port=McpSdkServerAdapter(),
        payload_repository_port=StaticPayloadRepository(),
        test_agent_port=AnthropicTestAgentAdapter() if with_dynamic_agent else None,
    )
