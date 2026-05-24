# ====================================================================================================
# server/routes/auth.py
# ====================================================================================================
"""
HDM AI - Authentication Routes
User login, Admin login, Register, Account delete
Users and admins can share the same email — they're separate accounts
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from config import settings
from schemas.core import RegisterRequest, LoginRequest, SuccessResponse
from models.core import User, APIKey, ThirdPartyKey
from middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(user_id: str, role: str = "user") -> str:
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


# ================================================================================================
# USER AUTH
# ================================================================================================

@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new USER account. Admins are created via CLI or admin panel."""
    existing = await User.find_one(
        User.email == request.email,
        User.role == "user"
    )
    if existing:
        raise HTTPException(400, "Email already registered as a user")

    user = User(
        email=request.email,
        username=request.username,
        hashed_password=pwd_context.hash(request.password),
        role="user",
    )
    await user.insert()
    token = create_token(str(user.id), "user")
    user.last_login = datetime.utcnow()
    await user.save()

    return {
        "success": True,
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRATION_HOURS * 3600,
            "role": "user",
        },
        "message": "Registration successful",
    }


@router.post("/login")
async def login(request: LoginRequest):
    """USER login — rejects admin accounts. Admins must use /auth/admin/login."""
    user = await User.find_one(
        User.email == request.email,
        User.role == "user"
    )
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(403, "Account deactivated")

    token = create_token(str(user.id), "user")
    user.last_login = datetime.utcnow()
    await user.save()

    return {
        "success": True,
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRATION_HOURS * 3600,
            "role": "user",
            "email": user.email,
            "username": user.username,
        },
        "message": "Login successful",
    }


# ================================================================================================
# ADMIN AUTH
# ================================================================================================

@router.post("/admin/login")
async def admin_login(request: LoginRequest):
    """ADMIN login — rejects regular user accounts. Users must use /auth/login."""
    user = await User.find_one(
        User.email == request.email,
        User.role == "admin"
    )
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(401, "Invalid admin credentials")
    if not user.is_active:
        raise HTTPException(403, "Admin account deactivated")

    token = create_token(str(user.id), "admin")
    user.last_login = datetime.utcnow()
    await user.save()

    return {
        "success": True,
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRATION_HOURS * 3600,
            "role": "admin",
            "email": user.email,
            "username": user.username,
        },
        "message": "Admin login successful",
    }


# ================================================================================================
# ACCOUNT MANAGEMENT
# ================================================================================================

@router.delete("/account")
async def delete_account(request: dict, user: dict = Depends(get_current_user)):
    """Permanently delete your own account and ALL associated data."""
    password = request.get("password")
    if not password:
        raise HTTPException(400, "Password required to confirm deletion")

    user_doc = await User.get(user["sub"])
    if not user_doc:
        raise HTTPException(404, "Account not found")
    if not pwd_context.verify(password, user_doc.hashed_password):
        raise HTTPException(401, "Incorrect password")

    user_id = str(user_doc.id)

    # Delete all outbound keys
    for key in await APIKey.find(APIKey.user_id == user_id).to_list():
        await key.delete()

    # Delete all inbound keys
    for key in await ThirdPartyKey.find(ThirdPartyKey.user_id == user_id).to_list():
        await key.delete()

    # Delete user
    await user_doc.delete()

    return {
        "success": True,
        "message": "Account and all associated data permanently deleted",
    }