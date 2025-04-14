from typing import List, Dict, Optional
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import re
from .super_bridge import Tool, ResourceType, ParameterSchema

class DiscoveryEngine:
    def __init__(self):
        self.cache: Dict = {}

    async def analyze_resource(self, resource: Dict, credentials: Dict) -> List[Tool]:
        """Analyze a resource and generate MCP tools."""
        async with aiohttp.ClientSession() as session:
            url = resource.get("url")
            resource_type = ResourceType(resource.get("type", "unknown"))
            tools = []
            if resource_type == ResourceType.API:
                tools.extend(await self.analyze_api(url, session, credentials))
            elif resource_type == ResourceType.STATIC:
                tools.extend(await self.scrape_static(url, session, credentials))
            elif resource_type == ResourceType.DATABASE:
                tools.append(self.mock_database_tool())
            elif resource_type == ResourceType.IOT:
                tools.append(self.mock_iot_tool())
            elif resource_type == ResourceType.SOCIAL:
                tools.append(self.mock_social_tool(url))
            return tools

    async def analyze_api(self, url: str, session: aiohttp.ClientSession, credentials: Dict) -> List[Tool]:
        """Analyze API resources."""
        openapi_spec = await self.fetch_openapi(url, session, credentials)
        tools = []
        if openapi_spec:
            paths = openapi_spec.get("paths", {})
            for path, methods in paths.items():
                for method, details in methods.items():
                    tool_name = path.replace("/", "_")[1:].replace("{", "_").replace("}", "")
                    tool = Tool(
                        name=f"{method}_{tool_name}",
                        path=path,
                        method=method.upper(),
                        description=details.get("summary", "No description"),
                        parameters=[
                            ParameterSchema(
                                name=param["name"],
                                type=param.get("schema", {}).get("type", "string"),
                                required=param.get("required", False)
                            )
                            for param in details.get("parameters", [])
                        ],
                        resource_type=ResourceType.API,
                        created_at=datetime.now(),
                        confidence=0.95
                    )
                    tools.append(tool)
        else:
            async with session.get(url, headers=credentials) as response:
                if "application/json" in response.headers.get("content-type", ""):
                    tools.append(Tool(
                        name="get_data",
                        path=url,
                        method="GET",
                        description=f"Fetches data from {url}",
                        parameters=[],
                        resource_type=ResourceType.API,
                        created_at=datetime.now(),
                        confidence=0.7
                    ))
        return tools

    async def scrape_static(self, url: str, session: aiohttp.ClientSession, credentials: Dict) -> List[Tool]:
        """Scrape static websites for tools."""
        tools = []
        async with session.get(url, headers=credentials) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            forms = soup.find_all("form")
            for form in forms:
                action = form.get("action", "")
                method = form.get("method", "get").upper()
                inputs = [
                    ParameterSchema(
                        name=inp.get("name"),
                        type=inp.get("type", "string"),
                        required=inp.get("required", False)
                    )
                    for inp in form.find_all("input")
                ]
                tool = Tool(
                    name=f"submit_{action.replace('/', '_')}",
                    path=action,
                    method=method,
                    description=f"Submits form at {action}",
                    parameters=inputs,
                    resource_type=ResourceType.STATIC,
                    created_at=datetime.now(),
                    confidence=0.8
                )
                tools.append(tool)
        return tools

    async def fetch_openapi(self, url: str, session: aiohttp.ClientSession, credentials: Dict) -> Optional[Dict]:
        endpoints = [f"{url}/openapi.json", f"{url}/swagger.json", f"{url}/api-docs"]
        for endpoint in endpoints:
            async with session.get(endpoint, headers=credentials) as response:
                if response.status == 200:
                    return await response.json()
        return None

    async def discover(self, query: str, tools: List[Tool]) -> List[Tool]:
        """Discover tools based on query."""
        matching_tools = []
        for tool in tools:
            score = 0
            if query.lower() in tool.description.lower():
                score += 0.5
            if query.lower() in tool.name.lower():
                score += 0.3
            if score > 0:
                tool.confidence = min(tool.confidence + score, 1.0)
                matching_tools.append(tool)
        return sorted(matching_tools, key=lambda x: x.confidence, reverse=True)

    async def learn_from_feedback(self, tool_name: str, success: bool, feedback: str, tools: List[Tool]):
        """Update tools based on feedback."""
        for tool in tools:
            if tool.name == tool_name:
                tool.confidence = min(tool.confidence + 0.1, 1.0) if success else max(tool.confidence - 0.1, 0.0)

    def mock_database_tool(self) -> Tool:
        """Placeholder for database tools."""
        return Tool(
            name="mock_db_query",
            path=None,
            method="POST",
            description="Mock database query",
            parameters=[ParameterSchema(name="query", type="string", required=True)],
            resource_type=ResourceType.DATABASE,
            created_at=datetime.now(),
            confidence=0.5
        )

    def mock_iot_tool(self) -> Tool:
        """Placeholder for IoT tools."""
        return Tool(
            name="mock_iot_control",
            path=None,
            method="POST",
            description="Mock IoT device control",
            parameters=[ParameterSchema(name="command", type="string", required=True)],
            resource_type=ResourceType.IOT,
            created_at=datetime.now(),
            confidence=0.5
        )

    def mock_social_tool(self, url: str) -> Tool:
        """Placeholder for social media tools."""
        return Tool(
            name="mock_social_fetch",
            path=url,
            method="GET",
            description=f"Fetches mock social media data from {url}",
            parameters=[],
            resource_type=ResourceType.SOCIAL,
            created_at=datetime.now(),
            confidence=0.5
        )
