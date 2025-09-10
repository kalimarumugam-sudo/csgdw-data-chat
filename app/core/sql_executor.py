from __future__ import annotations

from typing import Optional, Tuple

import duckdb  # type: ignore
import pandas as pd


def execute_sql_query(query: str, dataframe: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Execute a SQL query against the provided DataFrame using DuckDB.

    Returns a tuple of (result_dataframe, error_message). Exactly one will be None.
    """
    try:
        connection = duckdb.connect()
        connection.register("df", dataframe)
        result_df = connection.execute(query).df()
        connection.close()
        return result_df, None
    except Exception as exc:  # noqa: BLE001 - propagate as string for UI
        return None, str(exc)


