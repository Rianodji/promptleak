from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from promptleak.domain.entities import McpTool
from promptleak.domain.ports.mcp_server_port import McpServerPort
from promptleak.domain.value_objects import McpTargetConfig


class McpSdkServerAdapter(McpServerPort):
    """Implémente McpServerPort en parlant le protocole MCP réel (transport stdio)."""

    async def list_tools(self, target: McpTargetConfig) -> list[McpTool]:
        params = StdioServerParameters(command=target.command, args=list(target.args))

        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.list_tools()

        return [
            McpTool(
                name=tool.name,
                description=tool.description or "",
                input_schema=tool.inputSchema,
            )
            for tool in result.tools
        ]
