from facp import FACPSuperBridge

resources = [
    {"url": "http://api.example.com", "type": "api"},
    {"url": "mongodb://localhost:27017", "type": "database"},
    {"url": "mqtt://iot-device", "type": "iot"}
]

bridge = FACPSuperBridge(resources=resources, credentials={"Authorization": "Bearer your-token"})
mcp_app = bridge.create_mcp_server()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp_app, host="0.0.0.0", port=8001)
