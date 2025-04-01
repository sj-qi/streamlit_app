import io
import sys
from typing import Type
from pydantic import BaseModel
from config import CSV_FILE_PATH
from langchain.tools import BaseTool

# Input Code Schema
class PythonCodeInput(BaseModel):
    code: str

# Tool to run python code and provide analysis
class PythonExecutorTool(BaseTool):
    name: str = "python_executor_tool"
    description: str = "Executes Python code and returns the result."
    args_schema: Type[BaseModel] = PythonCodeInput

    def _run(self, code: str) -> str:
        
        code = code.strip().replace("```python", "").replace("```", "").strip()
        code = code.replace("CSV_FILE_PATH", f'"{CSV_FILE_PATH}"')

        exec_globals = {"__builtins__": __builtins__}
        exec_locals = {}

        stdout_backup = sys.stdout
        sys.stdout = io.StringIO()

        try:
            exec(code, exec_globals, exec_locals)
            output = sys.stdout.getvalue()

        except Exception as e:
            output = f"Execution failed: {str(e)}"
            
        finally:
            sys.stdout = stdout_backup

        return output if output else str(exec_locals)