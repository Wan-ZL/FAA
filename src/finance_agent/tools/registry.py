"""Tool registry with group-based loading and intent classification.

Tools are organized into groups by domain. An intent classifier (Haiku)
determines which groups to load based on the user's query, keeping the
tool context under 30K tokens.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """A single tool definition."""
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., Awaitable[Any]]

    def to_api_format(self) -> dict[str, Any]:
        """Convert to Anthropic API tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass
class ToolGroup:
    """A group of related tools loaded together."""
    name: str
    description: str
    tools: list[ToolDefinition] = field(default_factory=list)

    def register(self, tool: ToolDefinition) -> None:
        """Add a tool to this group."""
        self.tools.append(tool)


class ToolRegistry:
    """Central registry for all tools organized by group.

    Supports:
    - Group-based registration and loading
    - Intent-based tool selection
    - Core tools always loaded + domain tools on demand
    """

    def __init__(self) -> None:
        self._groups: dict[str, ToolGroup] = {}
        self._core_tools: list[ToolDefinition] = []
        self._all_handlers: dict[str, Callable[..., Awaitable[Any]]] = {}

    def register_group(self, group: ToolGroup) -> None:
        """Register a tool group."""
        self._groups[group.name] = group
        for tool in group.tools:
            self._all_handlers[tool.name] = tool.handler
        logger.info(f"Registered tool group '{group.name}' with {len(group.tools)} tools")

    def register_core_tool(self, tool: ToolDefinition) -> None:
        """Register a core tool (always loaded)."""
        self._core_tools.append(tool)
        self._all_handlers[tool.name] = tool.handler

    def get_tools_for_groups(
        self, group_names: list[str]
    ) -> tuple[list[dict[str, Any]], dict[str, Callable[..., Awaitable[Any]]]]:
        """Get tool definitions and handlers for specified groups + core tools.

        Returns:
            Tuple of (api_tool_definitions, handler_map)
        """
        tools: list[dict[str, Any]] = []
        handlers: dict[str, Callable[..., Awaitable[Any]]] = {}

        # Always include core tools
        for tool in self._core_tools:
            tools.append(tool.to_api_format())
            handlers[tool.name] = tool.handler

        # Add requested groups
        for name in group_names:
            group = self._groups.get(name)
            if group:
                for tool in group.tools:
                    tools.append(tool.to_api_format())
                    handlers[tool.name] = tool.handler

        return tools, handlers

    def get_all_tools(self) -> tuple[list[dict[str, Any]], dict[str, Callable[..., Awaitable[Any]]]]:
        """Get all registered tools."""
        return self.get_tools_for_groups(list(self._groups.keys()))

    def get_handler(self, tool_name: str) -> Callable[..., Awaitable[Any]] | None:
        """Get a specific tool handler by name."""
        return self._all_handlers.get(tool_name)

    def list_groups(self) -> dict[str, int]:
        """List all groups with tool counts."""
        return {name: len(group.tools) for name, group in self._groups.items()}


# Intent classifier prompt
INTENT_CLASSIFIER_PROMPT = """Classify which tool groups are needed for this query.
Return a JSON list of group names from:
["market_data", "fundamentals", "technical", "options", "macro", "sentiment", "risk_backtest"]

Rules:
- "market_data": any query mentioning stock prices, quotes, sectors, or market overview
- "fundamentals": valuation, earnings, financial statements, SEC filings
- "technical": chart patterns, indicators (RSI, MACD, etc.), support/resistance
- "options": options pricing, Greeks, strategies, implied volatility
- "macro": interest rates, GDP, inflation, economic indicators, FRED data
- "sentiment": news, social media, analyst ratings, insider trading
- "risk_backtest": risk metrics, VaR, Monte Carlo, backtesting, Sharpe ratio

Return ONLY a JSON array, nothing else."""


def tool(
    name: str,
    description: str,
    parameters: dict[str, Any],
) -> Callable:
    """Decorator to create a ToolDefinition from an async function."""
    def decorator(func: Callable[..., Awaitable[Any]]) -> ToolDefinition:
        return ToolDefinition(
            name=name,
            description=description,
            input_schema={
                "type": "object",
                "properties": parameters,
                "required": [k for k, v in parameters.items() if not v.get("optional", False)],
            },
            handler=func,
        )
    return decorator


# Singleton registry
tool_registry = ToolRegistry()
