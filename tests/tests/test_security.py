import pytest
from facp.security import SecurityModule

def test_jwt_creation():
    security = SecurityModule(secret_key="test-key")
    token = security.create_jwt({"sub": "test-user"})
    assert isinstance(token, str)
