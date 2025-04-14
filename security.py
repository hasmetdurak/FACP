from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from pydantic import BaseModel
import os

class TokenData(BaseModel):
    username: Optional[str] = None

class SecurityModule:
    def __init__(self, secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def create_jwt(self, data: dict) -> str:
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)

    async def verify_jwt(self, token: str) -> Optional[TokenData]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return TokenData(username=username)
        except JWTError:
            return None
