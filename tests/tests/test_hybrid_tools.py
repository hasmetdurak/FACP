import pytest
from facp.hybrid_tools import HybridToolGenerator
from facp.super_bridge import Tool, ResourceType
from datetime import datetime

@pytest.mark.asyncio
async def test_tool_execution():
    tool = Tool(
        name="static_tool",
        path=None,
        method="GET",
        description="Static tool",
        parameters=[],
        resource_type=ResourceType.STATIC,
        created_at=datetime.now(),
        confidence=0.8
    )
    generator = HybridToolGenerator([tool])
    result = await generator.execute_tool(tool, {}, {})
    assert result == "Static content processed"
