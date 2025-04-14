from fastapi import FastAPI, Depends, HTTPException
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
from .security import SecurityModule, TokenData
from .discovery_engine import DiscoveryEngine
from .hybrid_tools import HybridToolGenerator
from .connectors.mongodb import MongoDBConnector
from .connectors.aws_iot import AWSIoTConnector

class ResourceType(Enum):
    API = "api"
    DATABASE = "database"
    STATIC = "static"
    IOT = "iot"
    SOCIAL = "social"
    PHYSICAL = "physical"

class ParameterSchema(BaseModel):
    name: str
    type: str = "string"
    required: bool = False

class OutputSchema(BaseModel):
    result: dict = Field(..., description="Expected output structure")

class Tool(BaseModel):
    name: str
    path: Optional[str]
    method: str
    description: str
    parameters: List[ParameterSchema]
    resource_type: ResourceType
    created_at: datetime
    confidence: float
    output_schema: Optional[OutputSchema] = None

class FACPSuperBridge:
    def __init__(self, resources: List[Dict], credentials: Dict = None):
        self.resources = resources
        self.credentials = credentials or {}
        self.tools: List[Tool] = []
        self.security = SecurityModule()
        self.discovery_engine = DiscoveryEngine()
        self.hybrid_generator = HybridToolGenerator(self.tools)
        self.connectors = {
            "mongodb": MongoDBConnector,
            "aws_iot": AWSIoTConnector
        }

    async def initialize(self):
        """Initialize discovery and connector integration."""
        tasks = []
        for resource in self.resources:
            resource_type = resource.get("type")
            if resource_type in self.connectors:
                connector = self.connectors[resource_type](resource["url"], self.credentials)
                tasks.append(connector.generate_tools())
            else:
                tasks.append(self.discovery_engine.analyze_resource(resource, self.credentials))
        results = await asyncio.gather(*tasks)
        for tools in results:
            self.tools.extend(tools)
        self.hybrid_generator.update_tools(self.tools)

    async def discover(self, query: str) -> List[Tool]:
        """Discover tools based on AI query."""
        return await self.discovery_engine.discover(query, self.tools)

    async def learn_from_feedback(self, tool_name: str, success: bool, feedback: str):
        """Learn from AI feedback."""
        await self.discovery_engine.learn_from_feedback(tool_name, success, feedback, self.tools)
        self.hybrid_generator.update_tools(self.tools)

    def create_mcp_server(self) -> FastAPI:
        """Create an MCP server for AI agents."""
        mcp_app = FastAPI(title="FACP Super MCP Server")
        asyncio.create_task(self.initialize())

        async def get_current_user(token: str = Depends(self.security.oauth2_scheme)):
            token_data = await self.security.verify_jwt(token)
            if token_data is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            return token_data

        @mcp_app.get("/mcp/discover")
        async def discover_tools(query: str = "", user: TokenData = Depends(get_current_user)):
            return {"tools": await self.discover(query)}

        @mcp_app.post("/mcp/feedback")
        async def provide_feedback(tool_name: str, success: bool, feedback: str = "", user: TokenData = Depends(get_current_user)):
            await self.learn_from_feedback(tool_name, success, feedback)
            return {"status": "Feedback processed"}

        for tool in self.tools:
            async def dynamic_endpoint(user: TokenData = Depends(get_current_user), **kwargs):
                result = await self.hybrid_generator.execute_tool(tool, kwargs, self.credentials)
                return {"tool": tool.name, "result": result}
            mcp_app.get(f"/mcp/{tool.name}")(dynamic_endpoint)

        return mcp_app
