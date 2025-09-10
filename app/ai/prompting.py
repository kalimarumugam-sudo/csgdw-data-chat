from __future__ import annotations

from typing import Dict, List


def build_system_prompt(context: Dict[str, object]) -> str:
    schema_lines = [f"- {col}: {dtype}" for col, dtype in context["schema"].items()]
    return (
        "You are a helpful data analyst specializing in buy rates analysis.\n"
        "Focus on SQL-based analysis over a single in-memory table named df.\n\n"
        "Columns and types:\n" + "\n".join(schema_lines) + "\n\n"
        f"Row count: {context['row_count']}\n\n"
        "When you generate SQL, wrap it in ```sql fences and use proper DuckDB syntax."
    )


def prepare_messages(system_prompt: str, chat_messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [{"role": "system", "content": system_prompt}] + chat_messages


