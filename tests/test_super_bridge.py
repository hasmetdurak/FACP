import pytest
from facp.super_bridge import FACPSuperBridge, Tool, ResourceType
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_mcp_server_creation():
    resources = [{"url": "http://example.com", "type": "api"}]
    bridge = FACPSuperBridge(resources=resources)
    mcp_app = bridge.create_mcp_server()
    client = TestClient(mcp_app)
    response = client.get("/mcp/discover")
    assert response.status_code == 401  # Requires authentication
