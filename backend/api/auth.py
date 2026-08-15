from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

# Delegation to Security Framework
from backend.api_security.auth_flow import SimpleAuthFlow

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
auth_engine = SimpleAuthFlow()

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI Dependency to validate token and return user.
    """
    try:
        user = auth_engine.authenticate_request(f"Bearer {token}")
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
