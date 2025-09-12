import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_rates_data():
    """Load buy rates analysis data from CSV file"""
    csv_file = "data/csv/Buy Rates Analysis.csv"
    
    try:
        # Try to load from CSV file
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file,   sep=";", engine="python")
            # Ensure hire_date is datetime if it exists
            #if 'hire_date' in df.columns:
                #df['hire_date'] = pd.to_datetime(df['hire_date'])
            return df, None
        else:
            return None, f"CSV file '{csv_file}' not found. Please ensure the file exists in the application directory."
            
    except Exception as e:
        return None, f"Error loading CSV file: {str(e)}"


@st.cache_data
def load_data():
    """Main data loading function for buy rates analysis"""
    # Try to load from CSV
    df, error = load_rates_data()
    
    if df is not None:
        return df, f"✅ Loaded data from 'data/csv/Buy Rates Analysis.csv' ({len(df)} rows)", None
    else:
        # Return error state - no fallback data
        return None, None, error

def get_data_summary(df):
    """Get summary information about the loaded data"""
    summary = {
        'rows': len(df),
        'columns': list(df.columns),
        'data_types': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict()
    }
    return summary
