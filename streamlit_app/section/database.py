from section.utils.helper import engine1
import streamlit as st
from sqlalchemy import inspect
import pandas as pd

def _fetch_table_names():
    """Helper function to get table names."""
    inspector = inspect(engine1)
    return inspector.get_table_names()

def _display_tables(table_names):
    """Helper function to display tables."""
    if not table_names:
        st.warning("No tables found in the database.")
        return

    st.success(f"Found {len(table_names)} tables.")
    for table in table_names:
        with st.expander(f"📄 {table}"):
            try:
                df = pd.read_sql_table(table, con=engine1)
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error reading table {table}: {e}")

def database_page():
    """Displays the database page, including table listing and search."""
    st.title(":card_file_box: Database Tables")
    try:
        table_names = _fetch_table_names()
        _display_tables(table_names)  # Display tables

    except Exception as e:
        st.error(f"Failed to connect to the database or fetch tables: {e}")
