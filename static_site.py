from facp import FACPSuperBridge

resources = [
    {"url": "http://news-site.com", "type": "static"}
]

bridge = FACPSuperBridge(resources=resources, credentials={"Authorization": "Bearer your-token"})
mcp_app = bridge.create_mcp_server()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp_app, host="0.0.0.0", port=8001)
