# Data Chat App

A simple data chat application that demonstrates querying pandas DataFrames with SQL using DuckDB and Streamlit.

## Features

- 📊 Display data in an interactive table
- 🔍 Query pandas DataFrames using SQL syntax
- 💡 Pre-built example queries
- 📋 Schema information and sample values
- 🚀 Real-time query execution

## Quick Start (Streamlit)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run data_chat_app.py
```

3. Open your browser to the displayed URL (typically http://localhost:8501)

## How it Works

The app creates a sample employee dataset and allows you to query it using SQL. DuckDB enables direct SQL queries on the pandas DataFrame without needing a separate database.

## Sample Queries

Try these example queries:
- `SELECT * FROM df WHERE salary > 70000`
- `SELECT department, AVG(salary) FROM df GROUP BY department`
- `SELECT name, age FROM df WHERE department = 'Engineering' ORDER BY age`

## Next Steps

This is the foundation for adding LLM integration to convert natural language to SQL queries!

## Shiny for Python (New UI)

You can also run a Shiny-based UI that uses the same single DataFrame concept and AI orchestration.

1. Install dependencies (same requirements):
```bash
pip install -r requirements.txt
```

2. Ensure `OPENAI_API_KEY` is set in your environment (or an `.env` file).

3. Place `Buy Rates Analysis.csv` in the project root (semicolon-separated).

4. Run the Shiny app:
```bash
shiny run --reload shiny_app.py
```

This Shiny app separates concerns into `app/core` (DataFrame store and SQL executor), `app/ai` (orchestrator, prompts, LLM), and `app/tools` (pluggable tools such as SQL extraction). The UI lives in `app/ui/shiny_app.py`.