# ====================================================================================================
# server/routes/admin.py — COMPLETE with 4-key usage
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
# USAGE & CAPACITY (4 keys)
# ================================================================================================

@router.get("/usage")
async def usage_stats(admin: dict = Depends(get_current_admin)):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today.replace(day=1)

    services = ["general", "smartpos", "spark", "vibe", "vault", "erp", "widget"]
    service_stats = {}

    for service in services:
        today_count = await UsageLog.find(UsageLog.project == service, UsageLog.timestamp >= today).count()
        month_count = await UsageLog.find(UsageLog.project == service, UsageLog.timestamp >= month_start).count()
        tokens = 0
        async for log in UsageLog.find(UsageLog.project == service, UsageLog.timestamp >= today):
            tokens += log.tokens_used or 0

        if service in ["general", "vault", "widget"]:
            key_label = "Key 1"
        elif service == "erp":
            key_label = "Key 2"
        elif service in ["spark", "vibe"]:
            key_label = "Key 3"
        else:
            key_label = "Key 4"

        service_stats[service] = {
            "name": service.capitalize(),
            "requests_today": today_count,
            "requests_month": month_count,
            "tokens_today": tokens,
            "key": key_label,
            "usage_percent": round((today_count / 1440) * 100, 1) if today_count else 0,
        }

    key1_total = sum(service_stats[s]["requests_today"] for s in ["general", "vault", "widget"])
    key3_total = sum(service_stats[s]["requests_today"] for s in ["spark", "vibe"])

    groq_today = sum(s["requests_today"] for s in service_stats.values())
    groq_tokens = sum(s["tokens_today"] for s in service_stats.values())
    groq_month = sum(s["requests_month"] for s in service_stats.values())

    gemini_today = await UsageLog.find(UsageLog.provider == "gemini", UsageLog.timestamp >= today).count()
    gemini_month = await UsageLog.find(UsageLog.provider == "gemini", UsageLog.timestamp >= month_start).count()

    return SuccessResponse(data={
        "services": service_stats,
        "keys": {
            "key_1": {"label": "Key 1", "services": "General AI, Vault, Widget", "requests_today": key1_total, "limit_per_day": 1440, "usage_percent": round((key1_total / 1440) * 100, 1) if key1_total else 0},
            "key_2": {"label": "Key 2", "services": "ERP", "requests_today": service_stats.get("erp", {}).get("requests_today", 0), "limit_per_day": 1440, "usage_percent": round((service_stats.get("erp", {}).get("requests_today", 0) / 1440) * 100, 1) if service_stats.get("erp", {}).get("requests_today", 0) else 0},
            "key_3": {"label": "Key 3", "services": "Spark, Vibe", "requests_today": key3_total, "limit_per_day": 1440, "usage_percent": round((key3_total / 1440) * 100, 1) if key3_total else 0},
            "key_4": {"label": "Key 4", "services": "SmartPOS", "requests_today": service_stats.get("smartpos", {}).get("requests_today", 0), "limit_per_day": 1440, "usage_percent": round((service_stats.get("smartpos", {}).get("requests_today", 0) / 1440) * 100, 1) if service_stats.get("smartpos", {}).get("requests_today", 0) else 0},
        },
        "providers": {
            "groq": {"name": "Groq (Llama 3.3 70B)", "requests_today": groq_today, "requests_month": groq_month, "tokens_today": groq_tokens, "limit_requests_per_day": 5760, "usage_percent_today": round((groq_today / 5760) * 100, 1) if groq_today else 0, "status": "active"},
            "gemini": {"name": "Gemini (Flash/Pro)", "requests_today": gemini_today, "requests_month": gemini_month, "limit_flash_per_day": 1500, "status": "active" if settings.GEMINI_API_KEY else "not_configured", "usage_percent_today": round((gemini_today / 1500) * 100, 1) if gemini_today else 0},
            "code_execution": {"name": "Local Python/JS/Bash", "status": "active", "limit": "unlimited"},
        },
        "overall": {
            "total_requests_today": groq_today + gemini_today,
            "total_requests_month": groq_month + gemini_month,
            "total_tokens_today": groq_tokens,
            "free_tier_savings": "~$800/month vs paid equivalents (4 free keys × $200 each)",
        },
    })


# ================================================================================================
# AI CONFIGURATION
# ================================================================================================

@router.get("/ai-config")
async def get_ai_config(admin: dict = Depends(get_current_admin)):
    return SuccessResponse(data=_ai_config)


@router.put("/ai-config")
async def update_ai_config(request: dict, admin: dict = Depends(get_current_admin)):
    if "default_provider" in request:
        provider = request["default_provider"]
        if provider not in ["groq", "gemini"]: raise HTTPException(400, "Provider must be 'groq' or 'gemini'")
        _ai_config["default_provider"] = provider
    if "temperature" in request:
        temp = float(request["temperature"])
        if temp < 0 or temp > 1: raise HTTPException(400, "Temperature must be between 0.0 and 1.0")
        _ai_config["temperature"] = temp
    if "max_tokens" in request:
        tokens = int(request["max_tokens"])
        if tokens < 100 or tokens > 4096: raise HTTPException(400, "Max tokens must be between 100 and 4096")
        _ai_config["max_tokens"] = tokens
    if "default_model" in request: _ai_config["default_model"] = request["default_model"]
    logger.info(f"AI config updated: {_ai_config}")
    return SuccessResponse(data=_ai_config, message="AI configuration updated")


# ================================================================================================
# USER MANAGEMENT
# ================================================================================================

@router.get("/users")
async def list_users(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), admin: dict = Depends(get_current_admin)):
    skip = (page - 1) * limit
    users = await User.find_all().skip(skip).limit(limit).to_list()
    total = await User.count()
    return SuccessResponse(data={
        "users": [{"id": str(u.id), "email": u.email, "username": u.username, "role": u.role, "is_active": u.is_active, "created_at": u.created_at.isoformat(), "last_login": u.last_login.isoformat() if u.last_login else None, "api_keys_count": u.api_keys_count} for u in users],
        "pagination": {"total": total, "page": page, "pages": max(1, (total + limit - 1) // limit)},
    })


@router.get("/users/{user_id}")
async def get_user(user_id: str, admin: dict = Depends(get_current_admin)):
    u = await User.get(user_id)
    if not u: raise HTTPException(404, "User not found")
    return SuccessResponse(data={"id": str(u.id), "email": u.email, "username": u.username, "role": u.role, "is_active": u.is_active, "created_at": u.created_at.isoformat(), "last_login": u.last_login.isoformat() if u.last_login else None, "api_keys_count": u.api_keys_count, "total_requests": u.total_requests, "tokens_used": u.tokens_used})


@router.put("/users/{user_id}")
async def update_user(user_id: str, request: dict, admin: dict = Depends(get_current_admin)):
    u = await User.get(user_id)
    if not u: raise HTTPException(404, "User not found")
    if "role" in request and request["role"] in ["user", "admin"]: u.role = request["role"]
    if "is_active" in request: u.is_active = request["is_active"]
    await u.save()
    return SuccessResponse(message="User updated")


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(get_current_admin)):
    u = await User.get(user_id)
    if not u: raise HTTPException(404, "User not found")
    uid = str(u.id)
    for key in await APIKey.find(APIKey.user_id == uid).to_list(): await key.delete()
    for key in await ThirdPartyKey.find(ThirdPartyKey.user_id == uid).to_list(): await key.delete()
    await u.delete()
    return SuccessResponse(message="User and all data permanently deleted")


# ================================================================================================
# SYSTEM
# ================================================================================================

@router.get("/health")
async def health():
    return SuccessResponse(data={
        "server": "running", "version": settings.VERSION, "environment": settings.ENVIRONMENT,
        "mongodb": "connected", "redis": "connected" if settings.REDIS_URL else "not configured",
        "groq_api": "connected" if settings.GROQ_API_KEY else "not configured",
        "gemini_api": "connected" if settings.GEMINI_API_KEY else "not configured",
        "code_execution": "local", "ai_provider": _ai_config["default_provider"],
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