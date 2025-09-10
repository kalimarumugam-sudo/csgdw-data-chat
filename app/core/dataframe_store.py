from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
from shiny import reactive

from .sql_executor import execute_sql_query


@dataclass
class DataFrameStore:
    """Reactive holder for the application's canonical DataFrame.

    The store wraps a Shiny reactive.Value so UI elements redraw automatically
    when the DataFrame changes.
    """

    value: reactive.Value

    def get_dataframe(self) -> pd.DataFrame:
        return self.value.get()

    def set_dataframe(self, new_df: pd.DataFrame) -> None:
        self.value.set(new_df)

    def get_schema(self) -> Dict[str, str]:
        df = self.get_dataframe()
        return {col: str(dtype) for col, dtype in df.dtypes.items()}

    def get_sample_rows(self, n: int = 5) -> List[Dict[str, object]]:
        df = self.get_dataframe()
        return df.head(n).to_dict(orient="records")

    def get_row_count(self) -> int:
        return int(self.get_dataframe().shape[0])

    def apply_sql(self, sql: str) -> str | None:
        """Apply a SQL query to the current DataFrame, updating it on success.

        Returns an error message on failure, or None on success.
        """
        df = self.get_dataframe()
        result_df, error = execute_sql_query(sql, df)
        if error is not None:
            return error
        assert result_df is not None
        self.set_dataframe(result_df)
        return None


