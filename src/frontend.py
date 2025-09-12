import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from .data_loader import load_data
from .ai_service import USE_OPENAI, enhanced_query_handler
from .database_tools import (
    get_db_manager,
    get_db_status,
    set_db_status,
    init_database_connection,
    close_database_connection,
)

def enhance_data_processing(df):
    """Enhance data processing with date and numeric column conversion"""
    if df is None:
        return df
    
    # Convert date columns to datetime if they exist
    date_columns = ['Next Valid From', 'Next Valid Until']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Ensure numeric columns are properly formatted
    numeric_columns = ['Rate', 'Next Rate', 'Next Rate Diff', 'FP Diff', 'Proportion', 'Floor Price']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def create_dashboard_styling():
    """Add professional dashboard CSS styling"""
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .stApp > header {
        background-color: transparent;
    }
    .stApp {
        margin-top: 0;
    }
    .main .block-container {
        max-width: 100%;
    }
    .stImage {
        margin-bottom: 0rem;
    }
    .stTitle {
        margin-bottom: 0rem;
    }
    .stMarkdown {
        margin-top: 0rem;
        margin-bottom: 0rem;
    }
    .stMarkdown p {
        margin: 0.5rem 0 0 0 !important;
        padding: 0 !important;
    }
    .stPlotlyChart {
        margin-bottom: 0rem;
    }
    .stSubheader {
        margin-top: 0rem;
        margin-bottom: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

def create_kpi_metrics(data):
    """Create KPI metrics dashboard"""
    if data is None or data.empty:
        return
    
    # Use the actual column names from CSV
    rate_col = 'Rate'
    proportion_col = 'Proportion'
    supplier_col = 'Supplier'
    
    if rate_col not in data.columns:
        st.warning(f"Rate column not found. Available columns: {list(data.columns)}")
        return
    
    # Calculate KPIs from actual data
    total_records = len(data)
    avg_rate = data[rate_col].mean() if not data[rate_col].isna().all() else 0
    
    # Calculate revenue using Rate * Proportion
    if proportion_col in data.columns:
        total_revenue = (data[rate_col] * data[proportion_col]).sum()
    else:
        total_revenue = data[rate_col].sum()
    
    # Get unique suppliers
    unique_suppliers = data[supplier_col].nunique() if supplier_col in data.columns else 0
    
    # KPI metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Records",
            value=f"{total_records:,.0f}",
            delta="Active Dataset"
        )
    
    with col2:
        st.metric(
            label="Average Rate",
            value=f"${avg_rate:.2f}" if avg_rate > 0 else "N/A",
            delta="Current Period"
        )
    
    with col3:
        st.metric(
            label="Total Revenue",
            value=f"${total_revenue:,.0f}" if total_revenue > 0 else "N/A",
            delta="Calculated"
        )
    
    with col4:
        st.metric(
            label="Unique Suppliers",
            value=f"{unique_suppliers}",
            delta="Active"
        )

def create_visualizations(data):
    """Create interactive Plotly visualizations"""
    if data is None or data.empty:
        return
    
    rate_col = 'Rate'
    proportion_col = 'Proportion'
    supplier_col = 'Supplier'
    
    if rate_col not in data.columns:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 Suppliers by Volume grouped by Destination
        if supplier_col in data.columns and proportion_col in data.columns and 'Destination' in data.columns:
            try:
                # Calculate total volume by supplier and destination
                supplier_dest_volumes = data.groupby([supplier_col, 'Destination'])[proportion_col].sum().reset_index()
                
                # Get top 10 suppliers overall
                top_suppliers = data.groupby(supplier_col)[proportion_col].sum().nlargest(10).index
                
                # Filter to only show top 10 suppliers
                top_10_data = supplier_dest_volumes[supplier_dest_volumes[supplier_col].isin(top_suppliers)]
                
                if not top_10_data.empty:
                    # Create stacked bar chart
                    fig_supplier_dest = px.bar(
                        top_10_data,
                        x=supplier_col,
                        y=proportion_col,
                        color='Destination',
                        title='Top 10 Suppliers by Volume (Grouped by Destination)',
                        barmode='stack'
                    )
                    fig_supplier_dest.update_layout(height=400)
                    st.plotly_chart(fig_supplier_dest, use_container_width=True)
                else:
                    st.info("No supplier volume data available for visualization")
            except Exception as e:
                st.warning(f"Could not create supplier chart: {str(e)}")
        else:
            st.info("Required columns not available for supplier analysis")
    
    with col2:
        # Rate vs Floor Price scatter plot grouped by destination
        if 'Floor Price' in data.columns and 'Destination' in data.columns:
            try:
                # Filter out null values for better visualization
                plot_data = data.dropna(subset=['Floor Price', rate_col])
                
                if not plot_data.empty:
                    fig_rate_floor = px.scatter(
                        plot_data, 
                        x='Floor Price', 
                        y=rate_col, 
                        color='Destination',
                        title='Rate vs Floor Price by Destination',
                        hover_data=['Destination', 'Supplier', 'Product'] if 'Product' in data.columns else ['Destination', 'Supplier']
                    )
                    fig_rate_floor.update_layout(height=400)
                    st.plotly_chart(fig_rate_floor, use_container_width=True)
                else:
                    st.info("No valid rate/floor price data for visualization")
            except Exception as e:
                st.warning(f"Could not create rate comparison chart: {str(e)}")
        else:
            st.info("Floor Price or Destination column not available for comparison")

def ensure_oracle_connection():
    """Automatically connect to Oracle if not already connected"""
    if not get_db_status():
        try:
            if init_database_connection():
                set_db_status(True)
                st.success("✅ Connected to Oracle database")
                return True
        except Exception as e:
            st.error(f"❌ Failed to connect to Oracle: {str(e)}")
            return False
    return get_db_status()

def run_app():
    """Main function to run the Streamlit application"""
    # Streamlit app configuration
    st.set_page_config(
        page_title="Buy Rate Analysis Dashboard", 
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add dashboard styling
    create_dashboard_styling()

    # Load the data from external file
    df, success_message, error_message = load_data()

    # Check if data loaded successfully
    if df is not None:
        # Enhance data processing
        df = enhance_data_processing(df)
        # Initialize session state for current dataframe
        if 'current_df' not in st.session_state:
            st.session_state.current_df = df
    else:
        # Handle error case - no data loaded
        st.error(f"❌ Failed to load data: {error_message}")
        st.markdown("""
        **To use this application:**
        1. Ensure 'Buy Rates Analysis.csv' exists in the data/csv/ directory
        2. Check that the CSV file is properly formatted
        3. Restart the application after adding the file
        """)
        st.stop()  # Stop execution if no data

    # Create professional dashboard header
    header_container = st.container()
    with header_container:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.title("Buy Rate Analysis Dashboard")
            st.markdown("""
            <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 1.2rem; padding: 0;">
                Comprehensive Analysis & Insights with AI Chat
            </p>
            """, unsafe_allow_html=True)
        with col2:
            try:
                st.image("resources/logo.png", width=180)
            except:
                st.write("📊")  # Fallback if image not found
        
        # Horizontal line below the header
        st.markdown("---")
        
        # Show data loading status
        st.info(success_message)
    
    # Create KPI metrics dashboard
    if df is not None:
        create_kpi_metrics(st.session_state.current_df)

    # Initialize session state
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar - Chat Interface (Hideable)
    with st.sidebar:
        # Add logo if it exists
        try:
            st.image("resources/logo.png", width=200)
        except:
            pass  # If logo doesn't exist, just continue without it
        
        st.subheader("💬 CSG Digital Wholesale Data Chat")
        
        # Show current LLM provider
        provider_name = "🤖 OpenAI GPT-4" if USE_OPENAI else "🧠 AWS Bedrock Claude 3.5 Sonnet"
        st.info(f"**LLM Provider:** {provider_name}")
        
        st.write("Ask questions about your wholesale data - trends, comparisons, and insights!")
        
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
        if prompt := st.chat_input("Ask about your wholesale data (e.g., 'Show me rate trends' or 'Compare rates by category')"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Show user message in sidebar
            with chat_container:
                # Show user message
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Generate assistant response using enhanced handler (routes local vs Oracle)
                with st.chat_message("assistant"):
                    try:
                        # Ensure Oracle connection is available for database queries
                        ensure_oracle_connection()

                        # Use enhanced query handler (intelligent routing behind the scenes)
                        ai_response, sql_query, query_result, data_source = enhanced_query_handler(
                            prompt, st.session_state.current_df
                        )

                        # Display AI response
                        st.markdown(ai_response)

                        # If a SQL query produced results, show and apply them
                        if sql_query and query_result is not None and not isinstance(query_result, str):
                            st.code(sql_query, language="sql")
                            st.session_state.current_df = query_result
                            if data_source == "local":
                                st.success(f"✅ Local query executed! Updated table with {len(query_result)} rows.")
                            else:
                                st.success(f"✅ Oracle query executed! Updated table with {len(query_result)} rows.")
                            st.rerun()

                        # Persist assistant message
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})

                    except Exception as e:
                        error_msg = f"Error processing your request: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Main content area - Visualizations and Data Display
    st.subheader("📊 Interactive Visualizations")
    
    # Create visualizations
    if df is not None:
        create_visualizations(st.session_state.current_df)
    
    # Data Display Section
    st.subheader("📋 Data View")
    st.markdown("#### Data Table")
    
    # Display current data (either original or query results)
    st.dataframe(
        st.session_state.current_df, 
        use_container_width=True, 
        height=300,
        hide_index=True,
        key="data"
    )

if __name__ == "__main__":
    run_app()
