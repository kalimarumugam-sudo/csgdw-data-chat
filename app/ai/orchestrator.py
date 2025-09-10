from __future__ import annotations

from typing import Dict, Iterable, Iterator, List

from app.core.types import AssistantEvent, ToolContext
from app.tools.registry import ToolRegistry
from .llm_client import LlmClient
from .prompting import build_system_prompt, prepare_messages


class Orchestrator:
    def __init__(self, tools: ToolRegistry, model: str = "gpt-4") -> None:
        self._tools = tools
        self._llm = LlmClient(model=model)

    def _context_to_prompt(self, context: ToolContext) -> str:
        return build_system_prompt({
            "schema": context["schema"],
            "row_count": context["row_count"],
        })

    def stream_events(self, chat_messages: List[Dict[str, str]], context: ToolContext) -> Iterator[AssistantEvent]:
        system_prompt = self._context_to_prompt(context)
        messages = prepare_messages(system_prompt, chat_messages)

        # Proxy text stream to UI as "text" events
        stream = self._llm.stream(messages)
        accumulated_text = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if not delta:
                continue
            accumulated_text += delta
            yield {"type": "text", "data": {"text": delta}}

        # After stream ends, run sql tool to extract any SQL and emit an action if found
        if accumulated_text.strip():
            # Prefer sql tool auto-detection
            if "sql_query" in self._tools.list_tools():
                result = self._tools.run("sql_query", accumulated_text, context)
                if result.get("text"):
                    yield {"type": "text", "data": {"text": result["text"]}}
                if result.get("action"):
                    yield {"type": "action", "data": result["action"]}


