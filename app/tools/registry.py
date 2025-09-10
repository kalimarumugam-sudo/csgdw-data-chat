from __future__ import annotations

from typing import Dict, List

from app.core.types import ToolContext, ToolResult
from .base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def run(self, tool_name: str, user_text: str, context: ToolContext) -> ToolResult:
        tool = self._tools[tool_name]
        return tool.run(user_text, context)


