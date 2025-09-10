import streamlit as st
from dotenv import load_dotenv
from os import getenv
from openai import OpenAI
import re

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

def extract_sql_query(text):
    """Extract SQL query from LLM response"""
    # Look for SQL code blocks
    sql_pattern = r'```sql\s*(.*?)\s*```'
    match = re.search(sql_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Look for SELECT statements
    select_pattern = r'(SELECT.*?)(?:\n\n|$)'
    match = re.search(select_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    return None

def get_data_context():
    """Get context about the current dataset"""
    # Get current column information dynamically
    columns = list(st.session_state.current_df.columns)
    dtypes = st.session_state.current_df.dtypes.to_dict()
    
    column_info = []
    for col in columns:
        dtype_str = str(dtypes[col])
        if 'int' in dtype_str:
            column_info.append(f"- {col}: Integer values")
        elif 'float' in dtype_str:
            column_info.append(f"- {col}: Decimal/float values")
        elif 'datetime' in dtype_str:
            column_info.append(f"- {col}: Date/time values")
        elif 'object' in dtype_str:
            column_info.append(f"- {col}: Text/string values")
        else:
            column_info.append(f"- {col}: {dtype_str} values")
    
    return f"""
    You are helping with Buy Rates Analysis using the loaded dataset. 
    
    Current dataset columns and types:
    {chr(10).join(column_info)}
    
    Current dataset has {len(st.session_state.current_df)} rows.
    
    Focus on buy rate analysis queries such as:
    - Rate comparisons and trends
    - Performance analysis by different categories
    - Statistical summaries and insights
    - Compensation/salary analysis if salary data is present
    
    When generating SQL queries:
    1. Always use 'df' as the table name
    2. Wrap your SQL in ```sql code blocks
    3. Be specific about what the query does and how it helps with rate analysis
    4. Use proper SQL syntax for DuckDB
    5. Consider the actual column names and types shown above
    """

def get_ai_response(messages, model="gpt-4"):
    """Get response from OpenAI API"""
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        return stream
    except Exception as e:
        raise e

def create_system_message():
    """Create the system message for the AI assistant"""
    return {
        "role": "system", 
        "content": f"""You are a helpful data analyst specializing in buy rates analysis. {get_data_context()}
        
        When a user asks a question about buy rates data:
        1. Generate the appropriate SQL query for rate analysis
        2. Explain what the query does and how it helps with buy rate analysis
        3. Always format SQL queries in ```sql code blocks
        4. Provide insights about rate trends, patterns, and meaningful comparisons
        5. Focus on actionable insights from the buy rates data
        
        Be helpful and focus on buy rate analysis and data-driven insights.
        """
    }

def prepare_messages_for_api(chat_messages):
    """Prepare messages for OpenAI API with system context"""
    system_message = create_system_message()
    return [system_message] + [
        {"role": m["role"], "content": m["content"]}
        for m in chat_messages
    ]
