import streamlit as st

# API Keys for LLM
API_KEY = st.secrets["ANTHROPIC_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Database Credentials
DB_HOST = st.secrets["DB_HOST"]
DB_USER = st.secrets["DB_USER"]
DB_NAME = st.secrets["DB_NAME"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]

# Generic Variables
CSV_FILE_PATH = st.secrets["CSV_FILE_PATH"]
