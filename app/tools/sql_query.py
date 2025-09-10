from __future__ import annotations

import re
from typing import Optional

from app.core.types import Action, ToolContext, ToolResult


class SqlQueryTool:
    name = "sql_query"

    def _extract_sql(self, text: str) -> Optional[str]:
        # Prefer fenced code blocks
        match = re.search(r"```sql\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback to first SELECT statement until double newline/end
        match = re.search(r"(SELECT[\s\S]*?)(?:\n\n|$)", text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def run(self, user_text: str, context: ToolContext) -> ToolResult:
        sql = self._extract_sql(user_text)
        if not sql:
            guidance = (
                "Please provide a SQL query. Use df as the table name and wrap it in ```sql``` fences."
            )
            return {"text": guidance}

        action: Action = {"type": "sql", "payload": {"sql": sql}}
        return {
            "action": action,
            "text": f"""Executing SQL (rows: {context['row_count']}):
```sql
{sql}
```""",
        }


