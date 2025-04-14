from typing import List, Dict, Any
from pydantic import ValidationError
from .super_bridge import Tool, ResourceType, OutputSchema
import requests

class HybridToolGenerator:
    def __init__(self, tools: List[Tool]):
        self.tools = tools

    def update_tools(self, tools: List[Tool]):
        self.tools = tools

    async def execute_tool(self, tool: Tool, kwargs: Dict, credentials: Dict) -> Any:
        """Execute a tool with schema validation."""
        for param in tool.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Missing required parameter: {param.name}")

        if tool.resource_type == ResourceType.API:
            url = f"{tool.path}".format(**kwargs)
            try:
                response = requests.request(tool.method, url, params=kwargs, headers=credentials)
                result = response.json()
                if tool.output_schema:
                    tool.output_schema.validate({"result": result})
                return result
            except ValidationError as e:
                return {"error": f"Output validation failed: {str(e)}"}
            except Exception as e:
                return {"error": str(e)}
        elif tool.resource_type == ResourceType.STATIC:
            return "Static content processed"
        elif tool.resource_type == ResourceType.DATABASE:
            return "Database query executed"
        elif tool.resource_type == ResourceType.IOT:
            return "IoT command sent"
        elif tool.resource_type == ResourceType.SOCIAL:
            return "Social media data fetched"
        return "Not implemented"
