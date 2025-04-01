from typing import Type
import clickhouse_connect
from pydantic import BaseModel
from langchain.tools import BaseTool
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# Input Query Schema
class QueryInput(BaseModel):
    query: str

# Tool to validate queries and return Clickhouse compatible SQL
class ClickHouseQueryTool(BaseTool):
    name: str = "clickhouse_query_tool"
    description: str = "Use this to run SQL queries against the system error logs database."
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, query: str) -> str:

        client = clickhouse_connect.get_client(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        try:
            result = client.query_df(query)
            
            if result.empty:
                return "No results."
            return f"Data found: {len(result)} rows"

        except Exception as e:
            return f"Query failed: {str(e)}"