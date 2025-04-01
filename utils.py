import re
import streamlit as st
import clickhouse_connect
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# Fetch Data using Clickhouse
def fetch_csv_from_db(query):
    try:
        client = clickhouse_connect.get_client(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        return client.query_df(query)
    
    except Exception as e:
        st.error(f"❌ Query execution failed: {str(e)}")
        return None

# Cleanup function to reset Session States
def cleanup():
    if "dashboard_process" in st.session_state:
        st.session_state.dashboard_process.terminate()
        st.session_state.dashboard_generated = False
        del st.session_state["dashboard_process"]
        st.sidebar.success("🛑 Dashboard Stopped Successfully!")
        st.rerun()

# Clean Agent Thought Process
def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)