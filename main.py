# Import required libraries
import sys
import time
import subprocess
import webbrowser
import streamlit as st
from config import CSV_FILE_PATH
from langchain_anthropic import ChatAnthropic
from streamlit_autorefresh import st_autorefresh

# Import custom libraries
from tools.time_access_tool import TimeAccessTool
from agents.analysis_generator import analyze_errors
from agents.query_generator import generate_sql_query
from agents.followup_generator import provide_followup
from tools.python_executor_tool import PythonExecutorTool
from tools.clickhouse_query_tool import ClickHouseQueryTool
from utils import fetch_csv_from_db, cleanup, strip_ansi_codes

# Configure Streamlit layout settings
st.set_page_config(page_title="Error Analysis Dashboard", layout="wide")

# Initialize Claude model for LLM-based processing
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", max_tokens=8192, temperature=0.0)

# Define session state variables with default values
defaults = {
    "chat_history": [], 
    "thoughts": [],
    "user_input": "", 
    "fetched_data": None,
    "last_query": None,
    "last_raw_thought": None,
    "analysis_completed": False,
    "dashboard_generated": False,
    "new_data_available": False,
    "prev_row_count": 0,
    "last_data_check": 0
}

# Initialize session state variables if not already set
for key, val in defaults.items():
    st.session_state.setdefault(key, val)

# Enable auto-refresh every 60 seconds to check for new data
st_autorefresh(interval=60000, key="data_refresh")

# Track time since last data check
current_time = time.time()
time_since_last_check = current_time - st.session_state["last_data_check"]

# Sidebar - Input for querying error logs
st.sidebar.header("🔍 Load Error Logs from the database")
user_input = st.sidebar.text_input("Enter your request (e.g., 'fetch all logs for server 175'):")

# If there is a previous query, display it and check for new data
if st.session_state["last_query"]:
    with st.expander("🔍 View Generated SQL Query"):
        st.code(st.session_state["last_query"], language="sql")
        st.text_area("🧠 Agent's Thought Process", value=st.session_state.last_raw_thought.strip(), height=300)
    
    # Check if new data is available
    if time_since_last_check >= 60:
        try:
            new_data = fetch_csv_from_db(st.session_state["last_query"])
            new_row_count = len(new_data)
            
            if new_row_count > st.session_state["prev_row_count"]:
                st.session_state["new_data_available"] = True
                st.session_state["prev_row_count"] = new_row_count
                st.session_state["last_data_check"] = current_time

        except Exception as e:
            st.sidebar.error(f"⚠️ Error checking for new data: {str(e)}")

# Notify the user if new data is available
if st.session_state.get("new_data_available", False):
    st.sidebar.warning("🔄 New data available! Please press 'Fetch Data' to refresh.")
    st.session_state["new_data_available"] = False

# Button to fetch data and run analysis
if st.sidebar.button("Fetch Data & Run Analysis"):
    with st.spinner("Generating query..."):

        # Generate SQL query using LLM
        query, last_raw_thought = generate_sql_query(user_input, llm, [ClickHouseQueryTool(), TimeAccessTool()])
        query, last_raw_thought = query["output"], strip_ansi_codes(last_raw_thought)

        # Store query and agent's thought process
        st.session_state["last_query"] = query
        st.session_state["last_raw_thought"] = last_raw_thought
        
        # Initialize row count if this is the first query
        if st.session_state["prev_row_count"] == 0:
            st.session_state["prev_row_count"] = len(fetch_csv_from_db(query))
            st.session_state["last_data_check"] = time.time()
    
    with st.spinner("Fetching and analyzing data..."):
        try:
            data = fetch_csv_from_db(query)
            if data.empty:
                st.error("No data found. Please check your query and try again.")

            else:
                st.session_state["fetched_data"] = data
                st.session_state["new_data_available"] = False
                data.to_csv(CSV_FILE_PATH, index=False)
                st.success("✅ Data fetched successfully!")
                
                # Reset session state variables for new data processing
                if data is not None:
                    st.session_state.chat_history.clear()
                    st.session_state.thoughts.clear()
                    cleanup()
                    st.session_state.analysis_completed = st.session_state.dashboard_generated = False
                    st.session_state.pop("dashboard_process", None)
                    st.rerun()

        except Exception as e:
            st.error(f"Error fetching data: {str(e)}. Please check your query and try again.")

# Sidebar - Dashboard control buttons
st.sidebar.markdown("---")
st.sidebar.header("📊 Dashboard Controls")

if st.session_state.dashboard_generated:
    if st.sidebar.button("🚀 Open Dashboard", key="open_dash"):
        webbrowser.open("http://127.0.0.1:8050/", new=2)

    st.sidebar.button("🛑 Stop Dashboard", on_click=cleanup, key="stop_dash")

# Main UI title
st.title("📊 System Error Analysis Dashboard")

# Run error analysis if data is available and not yet analyzed
if st.session_state["fetched_data"] is not None and not st.session_state.analysis_completed:
    st.subheader("📄 Error Summary Report")
    
    with st.spinner("Analyzing error logs..."):
        response, raw_thoughts = analyze_errors(llm, [PythonExecutorTool(), TimeAccessTool()])
    
    # Store analysis results in session state
    st.session_state.chat_history.append(("Error Analysis Summary", response["output"]))
    st.session_state.thoughts.append(raw_thoughts)
    st.session_state.analysis_completed = True

    # Start the dashboard process
    dashboard_script_path = "dashboard.py"

    if not st.session_state.dashboard_generated:
        if "dashboard_process" in st.session_state:
            st.session_state.dashboard_process.terminate()
            del st.session_state["dashboard_process"]
    
    st.session_state.dashboard_process = subprocess.Popen([sys.executable, dashboard_script_path])
    st.session_state.dashboard_generated = True
    time.sleep(3)
    st.rerun()

# Display chat history with AI responses
for i, exchange in enumerate(st.session_state.chat_history):
    user_query, ai_response = exchange
    raw_thoughts = st.session_state.thoughts[i]
    clean_thoughts = strip_ansi_codes(raw_thoughts)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**🧑‍💻 You:** {user_query}")

    with col2:
        st.markdown(f"**🤖 AI:** {ai_response}")
        if clean_thoughts.strip():
            with st.expander("🧠 Agent's Thought Process", expanded=False):
                st.text_area("Agent Log", value=clean_thoughts.strip(), height=300)
                
    st.markdown("---")

# Handle follow-up user questions
def handle_input():
    user_question = st.session_state.user_input

    if user_question:
        with st.spinner("Thinking..."):
            response, raw_thoughts = provide_followup(user_question, llm, [PythonExecutorTool(), TimeAccessTool()], st.session_state.chat_history)

        st.session_state.chat_history.append((user_question, response["output"]))
        st.session_state.thoughts.append(raw_thoughts)
        st.session_state.user_input = ""

st.text_input("Ask a follow-up question:", key="user_input", on_change=handle_input)