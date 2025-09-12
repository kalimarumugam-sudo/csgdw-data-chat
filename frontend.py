import streamlit as st
import pandas as pd
from data_loader import load_data
from ai_service import extract_sql_query, get_ai_response, prepare_messages_for_api, USE_OPENAI

def execute_sql_query(query, dataframe):
    """Execute SQL query and return results"""
    import duckdb
    try:
        # Register the dataframe with DuckDB so it can be queried as 'df'
        conn = duckdb.connect()
        conn.register('df', dataframe)
        result = conn.execute(query).df()
        conn.close()
        return result, None
    except Exception as e:
        return None, str(e)

def run_app():
    """Main function to run the Streamlit application"""
    # Streamlit app configuration
    st.set_page_config(page_title="Rate Analysis", layout="wide")

    # Load the data from external file
    df, success_message, error_message = load_data()

    # Check if data loaded successfully
    if df is not None:
        # Initialize session state for current dataframe
        if 'current_df' not in st.session_state:
            st.session_state.current_df = df
    else:
        # Handle error case - no data loaded
        st.error(f"❌ Failed to load data: {error_message}")
        st.markdown("""
        **To use this application:**
        1. Ensure 'Buy Rates Analysis.csv' exists in the application directory
        2. Check that the CSV file is properly formatted
        3. Restart the application after adding the file
        """)
        st.stop()  # Stop execution if no data

    # Create a full-width header container that spans above sidebar and main content
    header_container = st.container()
    with header_container:
        # Center the title and add custom styling
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0; margin-bottom: 1rem;'>
                <h1 style='color: #262730; margin: 0; font-size: 2.5rem;'>Rate Analysis</h1>
            </div>
            <hr style='margin: 0 0 2rem 0; border: none; height: 2px; background-color: #f0f2f6;'>
        """, unsafe_allow_html=True)
        
        # Show data loading status
        st.info(success_message)

    # Initialize session state
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar - Chat Interface (Hideable)
    with st.sidebar:
        st.subheader("💬 Buy Rates Analysis Chat")
        
        # Show current LLM provider
        provider_name = "🤖 OpenAI GPT-4" if USE_OPENAI else "🧠 AWS Bedrock Claude 3.5 Sonnet"
        st.info(f"**LLM Provider:** {provider_name}")
        
        st.write("Ask questions about your buy rates data - trends, comparisons, and insights!")
        
        # Clear chat button at top
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        
        # Display chat history in the middle
        chat_container = st.container(height=400)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    # Chat input at the very bottom of sidebar
    with st.sidebar:
        # Chat input (positioned at bottom)
        if prompt := st.chat_input("Ask about your buy rates data (e.g., 'Show me rate trends' or 'Compare rates by category')"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Show user message in sidebar
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            # Generate assistant response
            with chat_container:
                with st.chat_message("assistant"):
                    # Prepare messages for OpenAI with system context
                    messages_for_api = prepare_messages_for_api(st.session_state.messages)
                    
                    # Get response from OpenAI
                    try:
                        stream = get_ai_response(messages_for_api, st.session_state["openai_model"])
                        response = st.write_stream(stream)
                        
                        # Add assistant response to chat history first
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        # Extract and execute SQL query if present
                        sql_query = extract_sql_query(response)
                        if sql_query:
                            st.write("**Executing query:**")
                            st.code(sql_query, language="sql")
                            
                            # Execute the query with current dataframe
                            result_df, error = execute_sql_query(sql_query, st.session_state.current_df)
                            if error:
                                st.error(f"Query execution failed: {error}")
                            else:
                                # Update the dataframe
                                st.session_state.current_df = result_df
                                st.success(f"✅ Query executed! Updated table with {len(result_df)} rows.")
                                st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        response = f"Sorry, I encountered an error: {str(e)}"
                        # Add error response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": response})

    # Main content area - Data Display
    st.subheader("📊 Data View")
    st.markdown("#### Data Table")
    
    # Display current data (either original or query results)
    st.dataframe(st.session_state.current_df, use_container_width=True, key="data")

if __name__ == "__main__":
    run_app()
