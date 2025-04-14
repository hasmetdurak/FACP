import pytest
from facp.connectors.mongodb import MongoDBConnector
from facp.super_bridge import Tool

@pytest.mark.asyncio
async def test_mongodb_connector():
    connector = MongoDBConnector("mongodb://localhost:27017")
    tools = await connector.generate_tools()
    assert isinstance(tools, list)
