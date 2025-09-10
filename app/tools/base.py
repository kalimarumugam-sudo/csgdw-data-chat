from __future__ import annotations

from typing import Protocol

from app.core.types import ToolContext, ToolResult


class Tool(Protocol):
    """Protocol for tools that can be called by the AI orchestrator."""

    name: str

    def run(self, user_text: str, context: ToolContext) -> ToolResult:  # noqa: D401 - simple interface
        """Run the tool given the user text and dataset context."""
        ...


