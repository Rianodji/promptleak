import asyncio
import sys
from pathlib import Path

import pytest

from promptleak.domain.value_objects import McpTargetConfig
from promptleak.infrastructure.adapters.mcp.mcp_sdk_server_adapter import McpSdkServerAdapter

CLEAN_SERVER_PATH = Path(__file__).parent.parent.parent / "labs" / "clean_server.py"


@pytest.mark.asyncio
async def test_lists_tools_exposed_by_the_clean_lab_server():
    target = McpTargetConfig(
        name="clean-lab-server",
        command=sys.executable,
        args=(str(CLEAN_SERVER_PATH),),
    )

    tools = await McpSdkServerAdapter().list_tools(target)

    tool_names = {tool.name for tool in tools}
    assert tool_names == {"add_numbers", "get_weather"}
    assert all(tool.description for tool in tools)
    assert all(tool.input_schema for tool in tools)


@pytest.mark.asyncio
async def test_list_tools_raises_for_a_nonexistent_command():
    target = McpTargetConfig(name="bad-target", command="/nonexistent/binary/xyz")

    with pytest.raises(Exception):  # noqa: B017 - exact SDK exception type is an implementation detail
        await asyncio.wait_for(McpSdkServerAdapter().list_tools(target), timeout=5)


@pytest.mark.asyncio
async def test_list_tools_raises_when_the_server_process_crashes_on_startup(tmp_path):
    crashing_server = tmp_path / "crashing_server.py"
    crashing_server.write_text("raise RuntimeError('boom')\n")
    target = McpTargetConfig(
        name="crashing-server", command=sys.executable, args=(str(crashing_server),)
    )

    with pytest.raises(Exception):  # noqa: B017 - exact SDK exception type is an implementation detail
        await asyncio.wait_for(McpSdkServerAdapter().list_tools(target), timeout=5)
