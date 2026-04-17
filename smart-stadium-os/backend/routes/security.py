"""
Security Routes for Elite Authentication.
Provides endpoints for JWT issuance and session management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from services.security_service import SecurityService
from services.cloud_logger import ops_logger as logger

router = APIRouter()

# For demo purposes, we use a static 'Master Admin' hashed password. 
# In a real enterprise system, this would be in a DB.
# Password: 'EliteStadium2026!'
MASTER_ADMIN_HASH = "$2b$12$ZqN.8f9j5n8f9j5n8f9j5eu3m5m5m5m5m5m5m5m5m5m5m5m5m5m5m" 

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user and returns a JWT token.
    Used for securing AI-critical endpoints.
    """
    # Note: In production, verify against MASTER_ADMIN_HASH from Secret Manager
    # For now, we simulate a successful login for the 'admin' user with 'stadium_elite' password
    if form_data.username == "admin" and form_data.password == "stadium_elite":
        access_token_expires = timedelta(minutes=60)
        access_token = SecurityService.create_access_token(
            data={"sub": form_data.username, "role": "ELITE_ADMIN"},
            expires_delta=access_token_expires
        )
        logger.info(f"Successful security login for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    
    logger.warning(f"Failed security login attempt for user: {form_data.username}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect neural credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
