from facp import FACPSuperBridge

resources = [
    {"url": "http://traffic-api.example.com", "type": "api"},
    {"url": "mqtt://smart-lights", "type": "iot"}
]

bridge = FACPSuperBridge(resources=resources, credentials={"Authorization": "Bearer your-token"})
mcp_app = bridge.create_mcp_server()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp_app, host="0.0.0.0", port=8001)
