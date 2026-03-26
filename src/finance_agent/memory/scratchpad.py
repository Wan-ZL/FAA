"""Per-agent scratchpad (in-memory working state).

Each agent gets a private scratchpad for intermediate calculations,
draft findings, and working state. Not shared, not persisted.
"""

from __future__ import annotations

from typing import Any


class AgentScratchpad:
    """Private working memory for a single agent instance.

    Used for:
    - Intermediate calculations (partial ratios, running tallies)
    - Draft findings being assembled before posting
    - Retrieved data being processed
    - Agent-specific context (tools called, items examined)
    """

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        self._store: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Store a value."""
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value."""
        return self._store.get(key, default)

    def has(self, key: str) -> bool:
        """Check if a key exists."""
        return key in self._store

    def delete(self, key: str) -> None:
        """Remove a key."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all working state."""
        self._store.clear()

    def keys(self) -> list[str]:
        """List all keys."""
        return list(self._store.keys())

    @property
    def size(self) -> int:
        """Number of items in scratchpad."""
        return len(self._store)
