import io
import contextlib
from langchain.schema import SystemMessage, HumanMessage
from langchain.agents import initialize_agent, AgentType

# Generates a ClickHouse SQL query based on user input using an AI agent
def generate_sql_query(user_input, llm, tools):
    
    system_prompt = f"""
                        You are an advanced analytical agent responsible for generating queries from a ClickHouse database based on user-inputs.
                        You can query the database using the 'clickhouse_query_tool' to validate whether the SQL query you've written is correct and whether the expected data exists.
                        Additionally, you can access the current date and time using the 'time_access_tool'. This tool will return the current date and time in a readable format whenever it is needed.

                        Database Table: 'zabbix_problems'
                        This table contains the following columns:
                        - 'hostname' (String): Hostname where the issue occurred  
                        - 'ip_address' (String): IP addesss of the host server 
                        - 'eventid' (String): Unique event id corresponding to problem
                        - 'full_problem_description' (String): Description of the problem  
                        - 'problem_time' (DateTime64): Time when the problem started  
                        - 'status' (String): Status of the issue. Possible values: 'Active', 'Resolved'  
                        - 'recovery_time' (Nullable DateTime64): [DO NOT INCLUDE] 
                        - 'duration' (Int32): Duration of issue in seconds. If unresolved, this is 0  
                        - 'severity_name' (String): Severity level  
                        - 'insert_time' (DateTime64): [DO NOT INCLUDE]

                        IMPORTANT CONSTRAINTS:
                            1. You can only use SELECT statements (no INSERT, UPDATE, DELETE, DROP, etc.)
                            2. Always apply filters after converting to lowercase
                            3. Do NOT use LIMIT unless explicitly requested by the user

                        You must follow this exact reasoning format:
                        Thought: Describe what you are trying to query  
                        Action: clickhouse_query_tool  
                        Action Input: <SQL query>  
                        Observation: <Tool result>  
                        Thought: Describe what the result means or what to do next ... (repeat if needed) 
                        Final Answer: <ONLY the final SQL query — no markdown, no comments, no explanation>

                        ⚠️ You must explicitly include the line **Final Answer:** before concluding your response, or the system will break.
                        Final Answer must ONLY contain the validated ClickHouse SQL query. Do not wrap it in backticks or markdown formatting. Do not explain it.
                    """
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        response = agent.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ],
            handle_parsing_errors=True
        )
        thoughts = buf.getvalue()
        
    return (response, thoughts)