import streamlit as st
from dotenv import load_dotenv
from os import getenv
from openai import OpenAI
import re
import pandas as pd
import duckdb
import json
import logging
import boto3
from botocore.exceptions import ClientError

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
USE_OPENAI = True
client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

# Option 2: AWS Bedrock (Uncomment these 3 lines to enable)
#USE_OPENAI = False
#from config.aws_config import aws_config, bedrock_config
#bedrock_client = aws_config.get_session().client('bedrock-runtime')
 
# Initialize OpenAI client placeholder; set when OpenAI is enabled
client = None
if USE_OPENAI:
    client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

def extract_sql_query(text):
    """Extract SQL query from LLM response (strips trailing semicolons)."""
    # Look for SQL code blocks
    sql_pattern = r'```sql\s*(.*?)\s*```'
    match = re.search(sql_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        query = match.group(1).strip()
        return query.rstrip(';')
    
    # Look for SELECT statements
    select_pattern = r'(SELECT.*?)(?:\n\n|$)'
    match = re.search(select_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        query = match.group(1).strip()
        return query.rstrip(';')
    
    return None

def get_data_context():
    """Get context about the current dataset (robust to non-Streamlit contexts)."""
    try:
        if hasattr(st.session_state, 'current_df') and st.session_state.current_df is not None:
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
        else:
            return """
            You are helping with data analysis. The current dataset information is not available.
            Focus on generating proper SQL queries for data analysis.
            """
    except:
        return """
        You are helping with data analysis. The current dataset information is not available.
        Focus on generating proper SQL queries for data analysis.
        """

def get_bedrock_response(messages, model_id=None):
    """Get response from AWS Bedrock Claude API"""
    try:
        from config.aws_config import bedrock_config
        
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

# -----------------------------------------------------------------------------
# Enhanced system/context and routing for local vs Oracle queries
# -----------------------------------------------------------------------------

def get_enhanced_system_message():
    """Create enhanced system message for both CSV and Oracle queries"""
    business_context = get_business_dictionary_context()
    
    return {
        "role": "system", 
        "content": f"""You are a helpful data analyst specializing in buy rates analysis and database queries. {get_data_context()}
        
        You can help with Oracle database queries. When users ask about:
        - Database tables, schemas, or structure
        - Oracle-specific queries
        - Database administration tasks
        - Business term queries (using business dictionary mappings)
        
        {business_context}
        
        IMPORTANT: When users ask questions using business terms:
        1. Use the business dictionary mappings to translate business terms to actual table.column names
        2. If a business term maps to a database field, use that exact table.column in your SQL
        3. Always use the full table name (schema.table) when referencing Oracle tables
        4. Use proper Oracle SQL syntax - NO SEMICOLONS at the end of queries
        5. For business users, EXCLUDE technical ID columns from results (like AGRTYPEID, CARRIERID, etc.)
        6. Focus on business-relevant columns like names, descriptions, dates, amounts, etc.
        7. Use SELECT with specific column names, avoiding SELECT * and ID columns
        8. Use proper Oracle data types and functions
        9. CRITICAL: If a business term has DISPLAY COLUMNS specified, use ONLY those columns in your SELECT clause
        10. CRITICAL: If a business term has JOIN instructions, follow them exactly for the FROM and JOIN clauses
        
        Oracle SQL Syntax Rules:
        - NO semicolons (;) at the end of queries
        - Use proper function names and date formats like TO_DATE('2023-01-01', 'YYYY-MM-DD')
        - Only use columns that exist in the actual table structure
        
        When a user asks a question:
        1. For CSV data: Generate appropriate SQL queries for rate analysis using DuckDB
        2. For Oracle database: Connect to Oracle and execute database queries
        3. Always explain what the query does and provide insights
        4. Format SQL queries in ```sql code blocks
        5. Focus on actionable insights from the data
        
        Be helpful and focus on data-driven insights from both local CSV and Oracle database.
        """
    }


def get_business_dictionary_context():
    """Get business dictionary context for AI consumption"""
    try:
        from .schema_service import SchemaService
        schema_service = SchemaService()
        business_dict = schema_service.load_business_dictionary()
        
        mappings = business_dict.get("mappings", [])
        if not mappings:
            return ""
        
        context_parts = ["Business Dictionary Mappings:"]
        for mapping in mappings[:20]:
            term = mapping.get("business_term", "")
            table = mapping.get("table_name", "")
            column = mapping.get("column_name", "")
            filter_condition = mapping.get("filter_condition", "")
            display_columns = mapping.get("display_columns", [])
            join_instructions = mapping.get("join_instructions", "")
            
            if filter_condition:
                context_parts.append(f"  - '{term}' -> {table}.{column} WHERE {filter_condition}")
            else:
                context_parts.append(f"  - '{term}' -> {table}.{column}")
            
            if display_columns:
                context_parts.append(f"    DISPLAY COLUMNS: {', '.join(display_columns)}")
            if join_instructions:
                context_parts.append(f"    JOIN: {join_instructions}")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        logger.error(f"Error getting business dictionary context: {e}")
        return ""


def get_ai_response_simple(user_message: str):
    """Get AI response for a single user message"""
    try:
        messages = [
            get_enhanced_system_message(),
            {"role": "user", "content": user_message}
        ]
        
        if USE_OPENAI:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                stream=False,
            )
            return response.choices[0].message.content
        else:
            response_text = get_bedrock_response(messages)
            return response_text
            
    except Exception as e:
        return f"Error getting AI response: {str(e)}"


def execute_sql_query(query, dataframe):
    """Execute SQL query on dataframe using DuckDB"""
    try:
        conn = duckdb.connect()
        conn.register('df', dataframe)
        result = conn.execute(query).fetchdf()
        conn.close()
        return result
    except Exception as e:
        return f"Error executing query: {str(e)}"


def enhanced_query_handler(user_message: str, dataframe):
    """Enhanced query handler that can use both local and Oracle data with business dictionary"""
    oracle_keywords = ['oracle', 'database', 'db', 'table', 'schema', 'sql server']
    is_oracle_query = any(keyword in user_message.lower() for keyword in oracle_keywords)
    
    if not is_oracle_query:
        try:
            from .schema_service import SchemaService
            schema_service = SchemaService()
            business_matches = schema_service.search_business_terms(user_message)
            if business_matches:
                is_oracle_query = True
                logger.info(f"Found business dictionary matches: {[m['business_term'] for m in business_matches]}")
        except Exception as e:
            logger.error(f"Error checking business dictionary: {e}")
    
    if is_oracle_query:
        try:
            from .database_tools import get_db_status, set_db_status, init_database_connection, get_db_manager
            if not get_db_status():
                if init_database_connection():
                    set_db_status(True)
            if get_db_status():
                ai_response = get_ai_response_simple(user_message)
                sql_query = extract_sql_query(ai_response)
                if sql_query:
                    db_manager = get_db_manager()
                    query_result = db_manager.execute_query(sql_query)
                    return ai_response, sql_query, query_result, "oracle"
                else:
                    return ai_response, None, None, "oracle"
            else:
                return "Oracle database is not connected. Please check your database configuration.", None, None, "oracle"
        except Exception as e:
            return f"Error with Oracle database: {str(e)}", None, None, "oracle"
    else:
        try:
            ai_response = get_ai_response_simple(user_message)
            sql_query = extract_sql_query(ai_response)
            if sql_query:
                query_result = execute_sql_query(sql_query, dataframe)
                return ai_response, sql_query, query_result, "local"
            else:
                return ai_response, None, None, "local"
        except Exception as e:
            return f"Error processing query: {str(e)}", None, None, "local"


# Oracle database helper wrappers
def get_oracle_tables():
    try:
        from .database_tools import get_db_manager
        db_manager = get_db_manager()
        return db_manager.get_tables_list()
    except Exception as e:
        return f"Error getting Oracle tables: {str(e)}"


def describe_oracle_table(table_name, schema_name=None):
    try:
        from .database_tools import get_db_manager
        db_manager = get_db_manager()
        return db_manager.describe_table(table_name, schema_name)
    except Exception as e:
        return f"Error describing Oracle table: {str(e)}"


def get_oracle_table_sample(table_name, limit=10, schema_name=None):
    try:
        from .database_tools import get_db_manager
        db_manager = get_db_manager()
        return db_manager.get_table_sample(table_name, limit, schema_name)
    except Exception as e:
        return f"Error getting Oracle table sample: {str(e)}"
