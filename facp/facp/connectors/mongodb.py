from pymongo import MongoClient
from typing import Dict, List
from ..super_bridge import Tool, ResourceType, ParameterSchema
from datetime import datetime

class MongoDBConnector:
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
        self.db = self.client.get_database()

    async def generate_tools(self) -> List[Tool]:
        tools = []
        collections = self.db.list_collection_names()
        for collection in collections:
            tools.append(Tool(
                name=f"query_{collection}",
                path=None,
                method="POST",
                description=f"Queries the {collection} collection",
                parameters=[ParameterSchema(name="query", type="string", required=True)],
                resource_type=ResourceType.DATABASE,
                created_at=datetime.now(),
                confidence=0.9
            ))
        return tools
