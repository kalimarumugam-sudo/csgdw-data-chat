"""
Rate Analysis Application Entry Point

This file serves as the main entry point for the Rate Analysis Streamlit application.
All frontend/UI code has been moved to frontend.py for better code organization.
"""

from frontend import run_app

if __name__ == "__main__":
    # Run the main Streamlit application
    run_app()
else:
    # When imported by Streamlit, execute the app directly
    run_app()
