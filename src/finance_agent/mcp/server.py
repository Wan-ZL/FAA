"""MCP Server exposing Finance Agent tools.

Auto-generates tool definitions from the Provider Registry and Tool Registry.
Supports both unified (single server) and domain-split configurations.

Tools use a {domain}_{action} naming convention:
- market_get_price, market_get_ohlcv
- fundamentals_get_income_stmt
- macro_get_fred
- sentiment_get_news
- options_get_chain
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from finance_agent.data.registry import registry as data_registry
from finance_agent.tools.registry import tool_registry

logger = logging.getLogger(__name__)


def create_mcp_server() -> Server:
    """Create and configure the MCP server with all tools."""
    server = Server("finance-agent")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        tools: list[Tool] = []

        # Get all tools from the tool registry
        api_tools, _ = tool_registry.get_all_tools()
        for t in api_tools:
            tools.append(Tool(
                name=t["name"],
                description=t.get("description", ""),
                inputSchema=t.get("input_schema", {"type": "object", "properties": {}}),
            ))

        # Also generate tools from the data registry
        for tool_def in data_registry.generate_mcp_tools():
            # Prefix with "data_" to avoid name collisions
            tools.append(Tool(
                name=f"data_{tool_def['name']}",
                description=tool_def.get("description", ""),
                inputSchema=tool_def.get("inputSchema", {"type": "object", "properties": {}}),
            ))

        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool call."""
        try:
            # Check tool registry first
            handler = tool_registry.get_handler(name)
            if handler:
                result = await handler(**arguments)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, default=str, indent=2),
                )]

            # Check data registry tools (prefixed with "data_")
            if name.startswith("data_get_"):
                data_type = name[len("data_get_"):]
                provider = arguments.pop("provider", None)
                result = await data_registry.fetch(data_type, provider=provider, **arguments)
                # Serialize Pydantic models
                serialized = [
                    r.model_dump() if hasattr(r, "model_dump") else r
                    for r in result
                ]
                return [TextContent(
                    type="text",
                    text=json.dumps(serialized, default=str, indent=2),
                )]

            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2),
            )]

        except Exception as e:
            logger.error(f"Tool {name} failed: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "tool_execution_failed",
                    "message": str(e),
                    "tool": name,
                }, indent=2),
            )]

    return server


async def run_mcp_server() -> None:
    """Run the MCP server over stdio."""
    server = create_mcp_server()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Entry point for the MCP server."""
    asyncio.run(run_mcp_server())


if __name__ == "__main__":
    main()
