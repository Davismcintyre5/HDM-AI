# ====================================================================================================
# server/middleware/auth.py
# ====================================================================================================
"""
HDM AI - Authentication Middleware
Validates JWT tokens (users + admins) and project API keys
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, Dict
from loguru import logger

from config import settings

security = HTTPBearer(auto_error=False)

PROJECT_KEYS: Dict[str, str] = {
    "general": settings.HDM_GENERAL_KEY,
    "smartpos": settings.HDM_SMARTPOS_KEY,
    "spark": settings.HDM_SPARK_KEY,
    "vibe": settings.HDM_VIBE_KEY,
    "vault": settings.HDM_VAULT_KEY,
    "erp": settings.HDM_ERP_KEY,
    "widget": settings.HDM_WIDGET_KEY,
}


class AuthMiddleware:
    """Authentication middleware for JWT and API keys."""

    @staticmethod
    async def authenticate_user(request: Request) -> dict:
        """Validate JWT token and return payload."""
        # Skip auth for OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return {"sub": None, "role": "user"}

        credentials: Optional[HTTPAuthorizationCredentials] = await security(request)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
            )

        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

    @staticmethod
    async def authenticate_admin(request: Request) -> dict:
        """Validate JWT token AND verify admin role."""
        # Skip auth for OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return {"sub": None, "role": "admin"}

        payload = await AuthMiddleware.authenticate_user(request)

        from models.core import User
        user = await User.get(payload.get("sub"))
        if not user or user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        return payload

    @staticmethod
    async def authenticate_project(request: Request, project: str) -> dict:
        """Validate project API key."""
        # Skip auth for OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return {"project": project, "authenticated": True}

        api_key = (
            request.headers.get("x-api-key")
            or request.headers.get("X-API-Key")
            or request.headers.get("Authorization", "").replace("Bearer ", "")
        )

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key",
            )

        expected_key = PROJECT_KEYS.get(project)
        if not expected_key or api_key != expected_key:
            logger.warning(f"Invalid API key for project: {project}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        return {"project": project, "authenticated": True}


# Dependency: Any authenticated user
async def get_current_user(request: Request) -> dict:
    return await AuthMiddleware.authenticate_user(request)


# Dependency: Admin only
async def get_current_admin(request: Request) -> dict:
    return await AuthMiddleware.authenticate_admin(request)


# Dependency: Project API key
def get_project_auth(project: str):
    async def _auth(request: Request) -> dict:
        return await AuthMiddleware.authenticate_project(request, project)
    return _auth