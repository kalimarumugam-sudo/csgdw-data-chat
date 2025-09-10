from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

from app.core.dataframe_store import DataFrameStore
from app.core.types import ToolContext
from app.tools.registry import ToolRegistry
from app.tools.sql_query import SqlQueryTool
from app.ai.orchestrator import Orchestrator


def load_initial_dataframe() -> pd.DataFrame:
    csv_path = Path("Buy Rates Analysis.csv")
    if not csv_path.exists():
        # Fallback to empty DataFrame if file missing
        return pd.DataFrame()
    # Use semicolon separator to match existing behavior
    return pd.read_csv(csv_path, sep=";", engine="python")


def make_tool_context(store: DataFrameStore) -> ToolContext:
    return {
        "schema": store.get_schema(),
        "sample_rows": store.get_sample_rows(5),
        "row_count": store.get_row_count(),
    }


def create_app() -> App:
    # Reactive state
    df_store = DataFrameStore(value=reactive.Value(load_initial_dataframe()))
    messages: reactive.Value[List[dict]] = reactive.Value([])

    # Tools and orchestrator
    registry = ToolRegistry()
    registry.register(SqlQueryTool())
    orchestrator = Orchestrator(registry, model="gpt-4")

    # UI layout (Shiny for Python sidebar page)
    app_ui = ui.page_sidebar(
        ui.sidebar(
            ui.input_action_button("clear", "Clear Chat"),
            ui.hr(),
            ui.input_text("prompt", "Ask about buy rates", placeholder="e.g. Compare rates by category"),
            ui.input_action_button("send", "Send"),
            ui.hr(),
            ui.output_text_verbatim("chat"),
        ),
        ui.h2("Rate Analysis (Shiny)"),
        ui.h4("Data View"),
        ui.output_data_frame("table"),
    )

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(input.clear)
        def _clear_chat() -> None:
            messages.set([])

        @reactive.effect
        @reactive.event(input.send)
        def _send_prompt() -> None:
            text = (input.prompt() or "").strip()
            if not text:
                return
            # Append user message
            msgs = messages.get() + [{"role": "user", "content": text}]
            messages.set(msgs)

            # Stream assistant events
            ctx = make_tool_context(df_store)
            for event in orchestrator.stream_events(msgs, ctx):
                if event["type"] == "text":
                    msgs = messages.get() + [{"role": "assistant", "content": event["data"]["text"]}]
                    messages.set(msgs)
                elif event["type"] == "action":
                    action = event["data"]
                    if action["type"] == "sql":
                        sql = action["payload"]["sql"]
                        error = df_store.apply_sql(sql)
                        if error:
                            msgs = messages.get() + [{"role": "assistant", "content": f"Query failed: {error}"}]
                            messages.set(msgs)
                        else:
                            # Refresh context after update
                            msgs = messages.get() + [{"role": "assistant", "content": "✅ Query executed and table updated."}]
                            messages.set(msgs)

        @output
        @render.data_frame
        def table():  # noqa: D401 - Shiny render
            return render.DataGrid(df_store.get_dataframe())

        @output
        @render.text
        def chat() -> str:
            # Simple concatenated chat log for demo; can be replaced with richer UI
            lines = []
            for m in messages.get():
                role = m["role"]
                content = m["content"].strip()
                if not content:
                    continue
                prefix = "You: " if role == "user" else "Assistant: "
                lines.append(prefix + content)
            return "\n\n".join(lines[-40:])

    return App(app_ui, server)


app = create_app()


