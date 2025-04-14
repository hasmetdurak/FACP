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
        asyncio.create_task(self.initialize
