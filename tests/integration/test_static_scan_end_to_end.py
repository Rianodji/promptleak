import sys
from pathlib import Path

import pytest

from promptleak.domain.services.static_analysis_service import StaticAnalysisService
from promptleak.domain.value_objects import McpTargetConfig
from promptleak.infrastructure.adapters.mcp.mcp_sdk_server_adapter import McpSdkServerAdapter
from promptleak.infrastructure.adapters.payloads.static_payload_repository import (
    StaticPayloadRepository,
)

LABS_DIR = Path(__file__).parent.parent.parent / "labs"


async def _scan(server_filename: str):
    target = McpTargetConfig(
        name=server_filename,
        command=sys.executable,
        args=(str(LABS_DIR / server_filename),),
    )
    tools = await McpSdkServerAdapter().list_tools(target)
    patterns = StaticPayloadRepository().load_static_patterns()
    return StaticAnalysisService().analyze(tools, patterns)


@pytest.mark.asyncio
async def test_clean_server_raises_no_finding():
    findings = await _scan("clean_server.py")

    assert findings == []


@pytest.mark.asyncio
async def test_poisoned_description_server_is_detected():
    findings = await _scan("poisoned_description_server.py")

    findings_by_tool = {f.tool_name for f in findings}
    assert "search_docs" in findings_by_tool
    assert "read_file" in findings_by_tool
    assert "translate_text" not in findings_by_tool

    techniques = {f.technique for f in findings}
    assert "exfiltration_request" in techniques
    assert "hidden_role_tag" in techniques
    assert "impersonated_system_instruction" in techniques
