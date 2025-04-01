import io
import contextlib
from config import CSV_FILE_PATH
from langchain.schema import SystemMessage, HumanMessage
from langchain.agents import initialize_agent, AgentType

# Analyzes system error logs stored in a CSV file and generates an error summary report
def analyze_errors(llm, tools):

    system_prompt = f"""
                        You are an advanced analytical agent responsible for analyzing system error logs stored in a CSV file located at: {CSV_FILE_PATH}.
                        You have access to a tool called 'python_executor_tool', which allows you to dynamically execute Python code on the CSV. You MUST use this tool to retrieve any data or perform any calculations. Do NOT make up numbers or summaries — use the tool to get real data.
                        Additionally, you can access the current date and time using the 'time_access_tool'. This tool will return the current date and time in a readable format whenever it is needed.
                        
                        For Python code execution:
                        - Always read the CSV from the path: '{CSV_FILE_PATH}'
                        - Use pandas to manipulate data
                        - Do not use any plotting libraries

                        Use your own intelligence only for:
                        - Providing suggestions and strategic recommendations
                        - Interpreting the data
                        - Anticipating potential follow-up questions

                        Database Table: 'zabbix_problems'
                        This table contains the following columns:
                        - 'hostname' (String): Hostname where the issue occurred 
                        - 'ip_address' (String): IP addesss of the host server 
                        - 'eventid' (String): Unique event id corresponding to problem 
                        - 'full_problem_description' (String): Description of the problem  
                        - 'problem_time' (DateTime64): Time when the problem started  
                        - 'status' (String): Status of the issue. Possible values: 'Active', 'Resolved'  
                        - 'duration' (Int32): Duration of issue in seconds. If unresolved, this is 0  
                        - 'severity_name' (String): Severity level  

                        You must follow this exact reasoning format:
                        Thought: Describe what you're trying to do next  
                        Action: python_executor_tool  
                        Action Input: <Python code (no markdown formatting)>  
                        Observation: <Tool's output>  
                        Thought: Describe what the result means or what to do next ... (repeat if needed)
                        Final Answer: <Full, plain-text summary with mitigation strategies and recommendations>  

                        ⚠️ You must explicitly include the line **Final Answer:** before concluding your response, or the system will break.
                        Format your response as **plain text only** — do not use markdown, JSON, or code blocks. The output should be a comprehensive, human-readable analysis based solely on the CSV file.
                    """

    human_prompt = f"""
                        The system error logs are stored in the provided CSV file path.
                        Format your response as **plain text only** — do not use markdown, JSON, or code blocks.

                        Error Summary Report:
                        1) Overview of Errors:
                            - Total number of errors
                            - Distribution of errors by severity (include count and percentages)
                            - Breakdown of issue statuses (e.g., Resolved, Active, Pending)
                            - Top 5 most frequent error messages (with occurrence counts)
                            - Average issue duration (in human-readable format)

                        2) Detailed Analysis:
                            - Error trends over time (hourly)
                            - Frequently recurring issues with patterns over problem_time (hourly)
                            - Any persistent or unresolved error types
                            - Component-level breakdown (which hosts/systems are most affected)
                            - Issue mitigation strategies

                        Output:
                            Don't make up data — infer only from the provided CSV file
                            Be clear and concise, avoid vague statements and quantify wherever possible
                            Format your response as **plain text only** — do not use markdown, JSON, or code blocks.          
                    """
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        response = agent.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ],
            handle_parsing_errors=True
        )
        thoughts = buf.getvalue()
        
    return (response, thoughts)