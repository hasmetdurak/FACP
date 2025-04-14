import pytest
from facp.discovery_engine import DiscoveryEngine
from facp.super_bridge import Tool, ResourceType
from datetime import datetime

@pytest.mark.asyncio
async def test_discovery():
    engine = DiscoveryEngine()
    tools = [Tool(
        name="test_tool",
        path="/test",
        method="GET",
        description="Test tool",
        parameters=[],
        resource_type=ResourceType.API,
        created_at=datetime.now(),
        confidence=0.9
    )]
    result = await engine.discover("test", tools)
    assert len(result) == 1
    assert result[0].name == "test_tool"
