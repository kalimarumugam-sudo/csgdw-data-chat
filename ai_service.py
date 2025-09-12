import streamlit as st
from dotenv import load_dotenv
from os import getenv
from openai import OpenAI
import re
import json
import boto3
from botocore.exceptions import ClientError

load_dotenv()

# =============================================================================
# LLM PROVIDER SELECTION - Comment/Uncomment to switch between providers
# =============================================================================
# 
# TO SWITCH PROVIDERS:
# 1. For OpenAI: Keep lines 25-26 uncommented, comment out lines 29-31
# 2. For Bedrock: Comment out lines 25-26, uncomment lines 29-31
#
# OpenAI uses: GPT-4 with streaming responses
# Bedrock uses: Claude 3.5 Sonnet (configured in .env file)
# =============================================================================

# Option 1: OpenAI (Comment out these 2 lines to disable)
#USE_OPENAI = True
#client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

# Option 2: AWS Bedrock (Uncomment these 3 lines to enable)
USE_OPENAI = False
from aws_config import aws_config, bedrock_config
bedrock_client = aws_config.get_session().client('bedrock-runtime')

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

def get_bedrock_response(messages, model_id=None):
    """Get response from AWS Bedrock Claude API"""
    try:
        from aws_config import bedrock_config
        
        # Use the LLM model ID from config (Claude 3.5 Sonnet)
        model_id = model_id or bedrock_config.llm_model_id
        
        # Convert messages to Claude format
        system_message = ""
        conversation_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Prepare request body for Claude with optimized settings
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.1,  # Lower temperature for more consistent SQL generation
            "top_p": 0.9,        # Focused responses
            "system": system_message,
            "messages": conversation_messages
        }
        
        # Get Bedrock client
        session = boto3.Session(
            profile_name=getenv('AWS_PROFILE', 'bedrock'),
            region_name=getenv('AWS_REGION', 'us-east-1')
        )
        bedrock_client = session.client('bedrock-runtime')
        
        # Call Bedrock
        response = bedrock_client.invoke_model(
            modelId=model_id,
            contentType='application/json',
            accept='application/json',
            body=json.dumps(body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        # Extract text content
        if 'content' in response_body and len(response_body['content']) > 0:
            return response_body['content'][0]['text']
        else:
            return "Sorry, I couldn't generate a response."
            
    except Exception as e:
        raise e

def get_ai_response(messages, model="gpt-4"):
    """Get response from configured LLM provider (OpenAI or Bedrock)"""
    try:
        if USE_OPENAI:
            # OpenAI API call with streaming
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )
            return stream
        else:
            # Bedrock API call (non-streaming for now)
            response_text = get_bedrock_response(messages)
            # Convert to generator for compatibility with Streamlit
            def text_generator():
                yield response_text
            return text_generator()
            
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
