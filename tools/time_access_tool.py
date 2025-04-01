import datetime
from typing import Optional
from langchain.tools import BaseTool

# Tool to access current date and time
class TimeAccessTool(BaseTool):
    name: str = "time_executor_tool"
    description: str = "Returns the current date and time. No input needed."
    args_schema: Optional[None] = None

    def _run(self, tool_input: str = "") -> str:
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")