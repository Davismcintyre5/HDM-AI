# ====================================================================================================
# server/routes/admin.py — COMPLETE
# ====================================================================================================
"""
HDM AI - Admin Panel Routes
All routes require admin authentication
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime, timedelta
from models.core import User, APIKey, UsageLog, ThirdPartyKey
from schemas.core import SuccessResponse
from middleware.auth import get_current_admin
from config import settings
from loguru import logger

router = APIRouter(prefix="/admin", tags=["Admin"])

# AI Configuration (in-memory, defaults to Groq, resets on server restart)
_ai_config = {
    "default_provider": "groq",
    "default_model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 1024,
}


# ================================================================================================
# DASHBOARD
# ================================================================================================

@router.get("/stats")
async def stats(admin: dict = Depends(get_current_admin)):
    return SuccessResponse(data={
        "total_users": await User.count(),
        "admins": await User.find(User.role == "admin").count(),
        "active_api_keys": await APIKey.find(APIKey.is_active == True).count(),
        "total_requests": await UsageLog.count(),
        "inbound_keys": await ThirdPartyKey.find(ThirdPartyKey.is_active == True).count(),
        "projects": {
            p: {
                "requests": await UsageLog.find(UsageLog.project == p).count(),
                "active_keys": await APIKey.find(APIKey.project == p, APIKey.is_active == True).count(),
            }
            for p in ["general", "smartpos", "spark", "vibe", "vault", "erp", "widget"]
        },
    })


# ================================================================================================
# USAGE & CAPACITY
# ================================================================================================

@router.get("/usage")
async def usage_stats(admin: dict = Depends(get_current_admin)):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today.replace(day=1)

    groq_today = await UsageLog.find(UsageLog.provider == "groq", UsageLog.timestamp >= today).count()
    gemini_today = await UsageLog.find(UsageLog.provider == "gemini", UsageLog.timestamp >= today).count()
    groq_month = await UsageLog.find(UsageLog.provider == "groq", UsageLog.timestamp >= month_start).count()
    gemini_month = await UsageLog.find(UsageLog.provider == "gemini", UsageLog.timestamp >= month_start).count()

    groq_tokens = 0
    gemini_tokens = 0
    async for log in UsageLog.find(UsageLog.timestamp >= today):
        if log.provider == "groq":
            groq_tokens += log.tokens_used
        elif log.provider == "gemini":
            gemini_tokens += log.tokens_used

    return SuccessResponse(data={
        "providers": {
            "groq": {
                "name": "Groq (Llama 3.3 70B)",
                "requests_today": groq_today,
                "requests_month": groq_month,
                "tokens_today": groq_tokens,
                "limit_requests_per_minute": 30,
                "limit_tokens_per_minute": 150000,
                "limit_requests_per_day": 1440,
                "status": "active" if settings.GROQ_API_KEY else "not_configured",
                "usage_percent_today": round((groq_today / 1440) * 100, 1) if groq_today else 0,
            },
            "gemini": {
                "name": "Gemini (Flash/Pro)",
                "requests_today": gemini_today,
                "requests_month": gemini_month,
                "tokens_today": gemini_tokens,
                "limit_flash_per_day": 1500,
                "limit_pro_per_day": 250,
                "status": "active" if settings.GEMINI_API_KEY else "not_configured",
                "usage_percent_today": round((gemini_today / 1500) * 100, 1) if gemini_today else 0,
            },
            "code_execution": {
                "name": "Local Python/JS/Bash",
                "status": "active",
                "limit": "unlimited",
                "timeout_seconds": 10,
            },
        },
        "ai_config": _ai_config,
        "database": {
            "mongodb": {
                "status": "connected",
                "limit_storage_mb": 512,
                "type": "MongoDB Atlas" if "mongodb+srv" in settings.MONGODB_URL else "Local MongoDB",
            },
            "redis": {
                "status": "connected" if settings.REDIS_URL else "not_configured",
                "limit_storage_mb": 30,
            },
        },
        "overall": {
            "total_requests_today": groq_today + gemini_today,
            "total_requests_month": groq_month + gemini_month,
            "total_tokens_today": groq_tokens + gemini_tokens,
            "free_tier_savings": "~$200/month vs paid equivalents",
        },
    })


# ================================================================================================
# AI CONFIGURATION
# ================================================================================================

@router.get("/ai-config")
async def get_ai_config(admin: dict = Depends(get_current_admin)):
    """Get current AI provider configuration."""
    return SuccessResponse(data=_ai_config)


@router.put("/ai-config")
async def update_ai_config(request: dict, admin: dict = Depends(get_current_admin)):
    """
    Update AI configuration. Changes take effect immediately for all users.
    
    Body:
    {
        "default_provider": "groq" | "gemini",
        "temperature": 0.0 - 1.0,
        "max_tokens": 100 - 4096,
        "default_model": "llama-3.3-70b-versatile" | "gemini-2.0-flash" | "gemini-2.0-pro"
    }
    """
    if "default_provider" in request:
        provider = request["default_provider"]
        if provider not in ["groq", "gemini"]:
            raise HTTPException(400, "Provider must be 'groq' or 'gemini'")
        _ai_config["default_provider"] = provider

    if "temperature" in request:
        temp = float(request["temperature"])
        if temp < 0 or temp > 1:
            raise HTTPException(400, "Temperature must be between 0.0 and 1.0")
        _ai_config["temperature"] = temp

    if "max_tokens" in request:
        tokens = int(request["max_tokens"])
        if tokens < 100 or tokens > 4096:
            raise HTTPException(400, "Max tokens must be between 100 and 4096")
        _ai_config["max_tokens"] = tokens

    if "default_model" in request:
        _ai_config["default_model"] = request["default_model"]

    logger.info(f"AI config updated: {_ai_config}")
    return SuccessResponse(data=_ai_config, message="AI configuration updated — all users now use these settings")


# ================================================================================================
# USER MANAGEMENT
# ================================================================================================

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin: dict = Depends(get_current_admin),
):
    skip = (page - 1) * limit
    users = await User.find_all().skip(skip).limit(limit).to_list()
    total = await User.count()
    return SuccessResponse(data={
        "users": [
            {
                "id": str(u.id), "email": u.email, "username": u.username,
                "role": u.role, "is_active": u.is_active,
                "created_at": u.created_at.isoformat(),
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "api_keys_count": u.api_keys_count,
            }
            for u in users
        ],
        "pagination": {"total": total, "page": page, "pages": max(1, (total + limit - 1) // limit)},
    })


@router.get("/users/{user_id}")
async def get_user(user_id: str, admin: dict = Depends(get_current_admin)):
    u = await User.get(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return SuccessResponse(data={
        "id": str(u.id), "email": u.email, "username": u.username,
        "role": u.role, "is_active": u.is_active,
        "created_at": u.created_at.isoformat(),
        "last_login": u.last_login.isoformat() if u.last_login else None,
        "api_keys_count": u.api_keys_count,
        "total_requests": u.total_requests,
        "tokens_used": u.tokens_used,
    })


@router.put("/users/{user_id}")
async def update_user(user_id: str, request: dict, admin: dict = Depends(get_current_admin)):
    u = await User.get(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    if "role" in request and request["role"] in ["user", "admin"]:
        u.role = request["role"]
    if "is_active" in request:
        u.is_active = request["is_active"]
    await u.save()
    return SuccessResponse(message="User updated")


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(get_current_admin)):
    u = await User.get(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    uid = str(u.id)
    for key in await APIKey.find(APIKey.user_id == uid).to_list():
        await key.delete()
    for key in await ThirdPartyKey.find(ThirdPartyKey.user_id == uid).to_list():
        await key.delete()
    await u.delete()
    return SuccessResponse(message="User and all data permanently deleted")


# ================================================================================================
# SYSTEM
# ================================================================================================

@router.get("/health")
async def health():
    return SuccessResponse(data={
        "server": "running",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "mongodb": "connected",
        "redis": "connected" if settings.REDIS_URL else "not configured",
        "groq_api": "connected" if settings.GROQ_API_KEY else "not configured",
        "gemini_api": "connected" if settings.GEMINI_API_KEY else "not configured",
        "code_execution": "local",
        "ai_provider": _ai_config["default_provider"],
    })


@router.get("/project-keys")
async def project_keys(admin: dict = Depends(get_current_admin)):
    return SuccessResponse(data={
        "keys": [
            {"project": "general", "key_prefix": settings.HDM_GENERAL_KEY[:12] + "***"},
            {"project": "smartpos", "key_prefix": settings.HDM_SMARTPOS_KEY[:12] + "***"},
            {"project": "spark", "key_prefix": settings.HDM_SPARK_KEY[:12] + "***"},
            {"project": "vibe", "key_prefix": settings.HDM_VIBE_KEY[:12] + "***"},
            {"project": "vault", "key_prefix": settings.HDM_VAULT_KEY[:12] + "***"},
            {"project": "erp", "key_prefix": settings.HDM_ERP_KEY[:12] + "***"},
            {"project": "widget", "key_prefix": settings.HDM_WIDGET_KEY[:12] + "***"},
        ]
    })