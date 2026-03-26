"""Core agent loop using Anthropic SDK.

Implements the 'while tool_calls' pattern: send messages to LLM,
execute any tool calls, append results, repeat until no more tool calls.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable, Awaitable

import anthropic

from finance_agent.config import settings

logger = logging.getLogger(__name__)

# Type alias for tool functions
ToolFunction = Callable[..., Awaitable[Any]]


class AgentLoop:
    """Core agent loop that manages conversation with Claude.

    Args:
        model: The Claude model to use
        system_prompt: System prompt for this agent
        tools: List of tool definitions (JSON schema format)
        tool_handlers: Map of tool name -> async handler function
        max_iterations: Maximum number of loop iterations
        max_tokens: Max tokens per LLM response
    """

    def __init__(
        self,
        model: str | None = None,
        system_prompt: str = "",
        tools: list[dict[str, Any]] | None = None,
        tool_handlers: dict[str, ToolFunction] | None = None,
        max_iterations: int = 25,
        max_tokens: int = 4096,
    ) -> None:
        self.model = model or settings.llm.worker_model
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.tool_handlers = tool_handlers or {}
        self.max_iterations = max_iterations
        self.max_tokens = max_tokens
        self.client = anthropic.AsyncAnthropic()
        self.messages: list[dict[str, Any]] = []
        self.total_tokens_used = 0

    async def run(self, user_message: str) -> str:
        """Run the agent loop with a user message.

        Returns the final text response from the agent.
        """
        self.messages.append({"role": "user", "content": user_message})

        for iteration in range(self.max_iterations):
            logger.debug(f"Agent loop iteration {iteration + 1}/{self.max_iterations}")

            # Call the LLM
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                tools=self.tools if self.tools else anthropic.NOT_GIVEN,
                messages=self.messages,
            )

            # Track token usage
            if response.usage:
                self.total_tokens_used += response.usage.input_tokens + response.usage.output_tokens

            # Append assistant response
            self.messages.append({"role": "assistant", "content": response.content})

            # Check if we need to process tool calls
            if response.stop_reason != "tool_use":
                # No tool calls - extract final text and return
                return self._extract_text(response.content)

            # Process tool calls
            tool_results = await self._process_tool_calls(response.content)
            self.messages.append({"role": "user", "content": tool_results})

        logger.warning(f"Agent loop reached max iterations ({self.max_iterations})")
        return self._extract_text(self.messages[-1].get("content", []) if self.messages else [])

    async def _process_tool_calls(
        self, content: list[Any]
    ) -> list[dict[str, Any]]:
        """Process all tool use blocks concurrently and return results."""
        # First pass: collect tool calls and their coroutines
        pending: list[tuple[str, str, asyncio.Task | None]] = []  # (tool_id, tool_name, coro|None)
        coros = []
        coro_indices: list[int] = []  # maps coro position -> pending index

        for block in content:
            if not (hasattr(block, "type") and block.type == "tool_use"):
                continue

            tool_name = block.name
            tool_input = block.input
            tool_id = block.id
            idx = len(pending)

            logger.info(f"Calling tool: {tool_name}({json.dumps(tool_input)[:200]})")

            handler = self.tool_handlers.get(tool_name)
            if handler is None:
                # No coroutine to run — record a None sentinel
                pending.append((tool_id, tool_name, None))
            else:
                pending.append((tool_id, tool_name, handler(**tool_input)))
                coros.append(pending[-1][2])
                coro_indices.append(idx)

        # Run all valid handler coroutines in parallel
        coro_results = await asyncio.gather(*coros, return_exceptions=True)

        # Second pass: package results
        results: list[dict[str, Any]] = []
        coro_pos = 0
        for idx, (tool_id, tool_name, coro) in enumerate(pending):
            if coro is None:
                # Unknown tool
                result: Any = {"error": f"Unknown tool: {tool_name}"}
            else:
                raw = coro_results[coro_pos]
                coro_pos += 1
                if isinstance(raw, BaseException):
                    logger.error(f"Tool {tool_name} failed: {raw}")
                    result = {
                        "error": "tool_execution_failed",
                        "message": str(raw),
                        "tool": tool_name,
                    }
                else:
                    result = raw

            # Serialize result
            if isinstance(result, str):
                content_str = result
            else:
                content_str = json.dumps(result, default=str)

            results.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": content_str,
            })
        return results

    @staticmethod
    def _extract_text(content: Any) -> str:
        """Extract text from response content blocks."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts = []
            for block in content:
                if hasattr(block, "type") and block.type == "text":
                    texts.append(block.text)
                elif isinstance(block, dict) and block.get("type") == "text":
                    texts.append(block.get("text", ""))
            return "\n".join(texts)
        return str(content)

    def reset(self) -> None:
        """Reset conversation state."""
        self.messages = []
        self.total_tokens_used = 0
