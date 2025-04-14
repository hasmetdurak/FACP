# Performance Optimization

FACP leverages async I/O for concurrent operations and supports load balancing via Docker Compose. Deploy multiple instances for high-traffic scenarios:
```bash
docker-compose up --scale facp=3
