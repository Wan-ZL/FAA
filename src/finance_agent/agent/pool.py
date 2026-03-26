"""Agent Pool with concurrency control.

Manages concurrent agent execution using asyncio.Semaphore
and a priority queue for task scheduling.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, TypeVar

from finance_agent.agent.models import Priority, TeammateTask

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AgentPool:
    """Controls concurrent agent execution.

    Uses a semaphore to limit the number of simultaneously running agents
    and a priority queue for scheduling.
    """

    def __init__(self, max_concurrent: int = 6) -> None:
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_count = 0
        self.completed_count = 0
        self.failed_count = 0

    async def submit(
        self,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Submit a task to the pool. Blocks if pool is full."""
        async with self.semaphore:
            self.active_count += 1
            try:
                result = await func(*args, **kwargs)
                self.completed_count += 1
                return result
            except Exception:
                self.failed_count += 1
                raise
            finally:
                self.active_count -= 1

    async def map(
        self,
        func: Callable[..., Awaitable[T]],
        items: list[Any],
        timeout: float | None = None,
    ) -> list[T | Exception]:
        """Run func on each item with concurrency control.

        Returns results in the same order as items.
        Failed tasks return the exception instead of raising.
        """
        async def _wrapped(item: Any) -> T:
            return await self.submit(func, item)

        coros = [_wrapped(item) for item in items]

        if timeout:
            results = await asyncio.wait_for(
                asyncio.gather(*coros, return_exceptions=True),
                timeout=timeout,
            )
        else:
            results = await asyncio.gather(*coros, return_exceptions=True)

        return results

    @property
    def stats(self) -> dict[str, int]:
        """Return pool statistics."""
        return {
            "active": self.active_count,
            "completed": self.completed_count,
            "failed": self.failed_count,
        }
