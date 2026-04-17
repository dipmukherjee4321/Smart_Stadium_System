"""
Security Service for Smart Stadium OS.
Handles JWT token generation, verification, and password hashing for Elite Auth.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from services.secret_service import secret_service
from services.cloud_logger import ops_logger as logger

# Configuration - Loaded from Secret Manager if possible
JWT_SECRET = secret_service.get_secret("JWT_SECRET_KEY") or "neural-stadium-bypass-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/security/login")

class SecurityService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({
            "exp": expire,
            "iss": "smart-stadium-os",
            "aud": "stadium-ops"
        })
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str):
        try:
            payload = jwt.decode(
                token, 
                JWT_SECRET, 
                algorithms=[ALGORITHM],
                audience="stadium-ops",
                issuer="smart-stadium-os"
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT Verification Failed: {e}")
            return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to protect routes with JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate neural credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = SecurityService.decode_token(token)
    if payload is None:
        raise credentials_exception
    return payload

# Singleton instance for general use
security_service = SecurityService()
