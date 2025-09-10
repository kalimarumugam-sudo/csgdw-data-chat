from __future__ import annotations

from typing import Any, Dict, Iterator, List, Literal, Optional, TypedDict


class Action(TypedDict):
    """Structured instruction emitted by the AI layer for the UI/core to apply.

    Examples:
    - {"type": "sql", "payload": {"sql": "SELECT * FROM df LIMIT 10"}}
    - {"type": "plot", "payload": {"figure_spec": {...}}}
    - {"type": "filter", "payload": {"where": "department = 'Sales'"}}
    """

    type: Literal["sql", "plot", "filter", "transform"]
    payload: Dict[str, Any]


class AssistantEvent(TypedDict):
    """Event produced by the AI orchestrator.

    - text: A message for the user
    - action: A structured action to apply to the DataFrame or UI
    """

    type: Literal["text", "action"]
    data: Dict[str, Any]


class ToolContext(TypedDict):
    """Context passed to tools about the current dataset."""

    schema: Dict[str, str]
    sample_rows: List[Dict[str, Any]]
    row_count: int


class ToolResult(TypedDict, total=False):
    """Result returned by a tool.

    At least one of (action, text) should be provided.
    """

    action: Action
    text: str


Messages = List[Dict[str, str]]


