# ====================================================================================================
# server/routes/api_keys.py
# ====================================================================================================
"""
HDM AI - API Key Routes
Outbound + Inbound + Admin, with api_structure support
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from loguru import logger

from models.core import APIKey, ThirdPartyKey, User, UserRole
from schemas.core import (
    OutboundKeyCreate, InboundKeyCreate, InboundKeyUpdate,
    AdminKeyCreate, AdminKeyUpdate, SuccessResponse,
)
from middleware.auth import get_current_user
from utils.token_generator import generate_api_key, hash_api_key
from utils.encryption import encrypt_key, decrypt_key

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

PREFIXES = {
    "general": "hdm_gen_", "smartpos": "hdm_pos_", "spark": "hdm_spk_",
    "vibe": "hdm_vib_", "vault": "hdm_vlt_", "erp": "hdm_erp_", "widget": "hdm_wdg_",
}

KNOWN_URLS = {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "google": "https://generativelanguage.googleapis.com/v1beta",
}


# ================================================================================================
# HELPERS
# ================================================================================================

async def _require_admin(user: dict):
    admin = await User.get(user["sub"])
    if not admin or admin.role != UserRole.ADMIN:
        raise HTTPException(403, "Admin access required")
    return admin


# ================================================================================================
# OUTBOUND — USER
# ================================================================================================

@router.post("/outbound")
async def create_outbound(request: OutboundKeyCreate, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    user_doc = await User.get(user_id)

    if user_doc and user_doc.role != UserRole.ADMIN:
        if request.project != "general":
            raise HTTPException(403, "Only General AI keys available")

    prefix = PREFIXES.get(request.project)
    if not prefix:
        raise HTTPException(400, f"Invalid project: {request.project}")

    full_key = generate_api_key(prefix)
    key = APIKey(
        user_id=user_id, project=request.project,
        key_prefix=full_key[:12] + "...", full_key_hash=hash_api_key(full_key),
        name=request.name,
    )
    await key.insert()

    if user_doc:
        user_doc.api_keys_count = await APIKey.find(
            APIKey.user_id == user_id, APIKey.is_active == True
        ).count()
        await user_doc.save()

    return {
        "success": True,
        "data": {
            "id": str(key.id), "project": key.project, "key_prefix": key.key_prefix,
            "name": key.name, "is_active": True, "created_at": key.created_at.isoformat(),
            "full_key": full_key,
        },
        "message": "Key created — save it now!",
    }


@router.get("/outbound")
async def list_outbound(user: dict = Depends(get_current_user)):
    keys = await APIKey.find(
        APIKey.user_id == user["sub"], APIKey.is_active == True
    ).sort(-APIKey.created_at).to_list()

    return {
        "success": True,
        "data": [
            {
                "id": str(k.id), "project": k.project, "key_prefix": k.key_prefix,
                "name": k.name, "is_active": k.is_active,
                "last_used": k.last_used.isoformat() if k.last_used else None,
                "total_requests": k.total_requests, "tokens_used": k.tokens_used,
                "created_at": k.created_at.isoformat(),
            }
            for k in keys
        ],
    }


@router.delete("/outbound/{key_id}")
async def delete_outbound(key_id: str, user: dict = Depends(get_current_user)):
    key = await APIKey.get(key_id)
    if not key or key.user_id != user["sub"]:
        raise HTTPException(404, "Key not found")
    await key.delete()
    user_doc = await User.get(user["sub"])
    if user_doc:
        user_doc.api_keys_count = await APIKey.find(
            APIKey.user_id == user["sub"], APIKey.is_active == True
        ).count()
        await user_doc.save()
    return {"success": True, "message": "Key permanently deleted"}


# ================================================================================================
# INBOUND — USER
# ================================================================================================

@router.post("/inbound")
async def create_inbound(request: InboundKeyCreate, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    encrypted = encrypt_key(request.api_key)
    base_url = request.base_url or KNOWN_URLS.get(request.provider)

    key = ThirdPartyKey(
        user_id=user_id, provider=request.provider, name=request.name,
        encrypted_key=encrypted, base_url=base_url,
        api_structure=request.api_structure,
    )
    await key.insert()

    return {
        "success": True,
        "data": {
            "id": str(key.id), "provider": key.provider, "name": key.name,
            "key_prefix": "••••" + request.api_key[-4:],
            "base_url": key.base_url, "api_structure": key.api_structure,
            "is_active": True, "is_verified": False,
            "created_at": key.created_at.isoformat(),
        },
        "message": "External key stored securely",
    }


@router.get("/inbound")
async def list_inbound(user: dict = Depends(get_current_user)):
    keys = await ThirdPartyKey.find(
        ThirdPartyKey.user_id == user["sub"], ThirdPartyKey.is_active == True
    ).sort(-ThirdPartyKey.created_at).to_list()

    return {
        "success": True,
        "data": [
            {
                "id": str(k.id), "provider": k.provider, "name": k.name,
                "key_prefix": "••••" + decrypt_key(k.encrypted_key)[-4:],
                "base_url": k.base_url, "api_structure": k.api_structure,
                "is_active": k.is_active, "is_verified": k.is_verified,
                "last_tested": k.last_tested.isoformat() if k.last_tested else None,
                "test_result": k.test_result,
                "created_at": k.created_at.isoformat(),
                "updated_at": k.updated_at.isoformat(),
            }
            for k in keys
        ],
    }


@router.put("/inbound/{key_id}")
async def update_inbound(key_id: str, request: InboundKeyUpdate, user: dict = Depends(get_current_user)):
    key = await ThirdPartyKey.get(key_id)
    if not key or key.user_id != user["sub"]:
        raise HTTPException(404, "Key not found")

    if request.name is not None: key.name = request.name
    if request.api_key is not None: key.encrypted_key = encrypt_key(request.api_key)
    if request.base_url is not None: key.base_url = request.base_url
    if request.api_structure is not None: key.api_structure = request.api_structure
    if request.is_active is not None: key.is_active = request.is_active

    key.updated_at = datetime.utcnow()
    await key.save()
    return {"success": True, "message": "Key updated"}


@router.delete("/inbound/{key_id}")
async def delete_inbound(key_id: str, user: dict = Depends(get_current_user)):
    key = await ThirdPartyKey.get(key_id)
    if not key or key.user_id != user["sub"]:
        raise HTTPException(404, "Key not found")
    await key.delete()
    return {"success": True, "message": "Key permanently deleted"}


@router.post("/inbound/{key_id}/test")
async def test_inbound(key_id: str, user: dict = Depends(get_current_user)):
    import httpx, time

    key = await ThirdPartyKey.get(key_id)
    if not key or key.user_id != user["sub"]:
        raise HTTPException(404, "Key not found")

    decrypted = decrypt_key(key.encrypted_key)
    url = key.base_url
    if not url:
        raise HTTPException(400, "No base URL set")

    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers={"Authorization": f"Bearer {decrypted}"})
            elapsed = (time.time() - start) * 1000
            success = resp.status_code < 400
            key.last_tested = datetime.utcnow()
            key.is_verified = success
            key.test_result = f"HTTP {resp.status_code}"
            await key.save()
            return {
                "success": True,
                "data": {
                    "success": success, "status_code": resp.status_code,
                    "message": f"{'Connected' if success else 'Failed'} — HTTP {resp.status_code}",
                    "response_time_ms": round(elapsed, 2),
                },
            }
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        key.last_tested = datetime.utcnow()
        key.is_verified = False
        key.test_result = str(e)[:100]
        await key.save()
        return {
            "success": True,
            "data": {
                "success": False,
                "message": f"Connection failed: {str(e)[:200]}",
                "response_time_ms": round(elapsed, 2),
            },
        }


# ================================================================================================
# ADMIN OUTBOUND — Full access to all keys across all users and projects
# ================================================================================================

@router.get("/admin/outbound")
async def admin_list_outbound(
    project: str = Query(None),
    user_id: str = Query(None),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin: dict = Depends(get_current_user),
):
    await _require_admin(admin)

    query = {}
    if project: query["project"] = project
    if user_id: query["user_id"] = user_id
    if status == "active": query["is_active"] = True
    elif status == "revoked": query["is_active"] = False

    skip = (page - 1) * limit
    keys = await APIKey.find(query).skip(skip).limit(limit).sort(-APIKey.created_at).to_list()
    total = await APIKey.find(query).count()

    # Get user emails
    user_ids = list(set(k.user_id for k in keys))
    users = await User.find({"$or": [{"_id": uid} for uid in user_ids]}).to_list() if user_ids else []
    user_map = {str(u.id): u.email for u in users}

    return {
        "success": True,
        "data": {
            "keys": [
                {
                    "id": str(k.id), "user_id": k.user_id,
                    "user_email": user_map.get(k.user_id, "Unknown"),
                    "project": k.project, "key_prefix": k.key_prefix,
                    "name": k.name, "is_active": k.is_active,
                    "last_used": k.last_used.isoformat() if k.last_used else None,
                    "total_requests": k.total_requests, "tokens_used": k.tokens_used,
                    "created_at": k.created_at.isoformat(),
                }
                for k in keys
            ],
            "pagination": {"total": total, "page": page, "pages": max(1, (total + limit - 1) // limit)},
        },
    }


@router.post("/admin/outbound")
async def admin_create_outbound(request: AdminKeyCreate, admin: dict = Depends(get_current_user)):
    await _require_admin(admin)

    prefix = PREFIXES.get(request.project)
    if not prefix:
        raise HTTPException(400, f"Invalid project: {request.project}")

    full_key = generate_api_key(prefix)
    key = APIKey(
        user_id=request.user_id, project=request.project,
        key_prefix=full_key[:12] + "...", full_key_hash=hash_api_key(full_key),
        name=request.name,
    )
    await key.insert()
    return {
        "success": True,
        "data": {"id": str(key.id), "user_id": key.user_id, "project": key.project, "full_key": full_key},
        "message": "Key created",
    }


@router.put("/admin/outbound/{key_id}")
async def admin_update_outbound(key_id: str, request: AdminKeyUpdate, admin: dict = Depends(get_current_user)):
    await _require_admin(admin)
    key = await APIKey.get(key_id)
    if not key:
        raise HTTPException(404, "Key not found")
    if request.name is not None: key.name = request.name
    if request.is_active is not None: key.is_active = request.is_active
    if request.project and request.project in PREFIXES: key.project = request.project
    await key.save()
    return {"success": True, "message": "Key updated"}


@router.delete("/admin/outbound/{key_id}")
async def admin_delete_outbound(key_id: str, admin: dict = Depends(get_current_user)):
    await _require_admin(admin)
    key = await APIKey.get(key_id)
    if key:
        await key.delete()
    return {"success": True, "message": "Key permanently deleted"}


@router.post("/admin/outbound/{key_id}/rotate")
async def admin_rotate_key(key_id: str, admin: dict = Depends(get_current_user)):
    await _require_admin(admin)
    old = await APIKey.get(key_id)
    if not old:
        raise HTTPException(404, "Key not found")

    prefix = PREFIXES.get(old.project, "hdm_gen_")
    full_key = generate_api_key(prefix)
    new_key = APIKey(
        user_id=old.user_id, project=old.project,
        key_prefix=full_key[:12] + "...", full_key_hash=hash_api_key(full_key),
        name=f"{old.name} (rotated)",
    )
    await new_key.insert()
    await old.delete()
    return {
        "success": True,
        "data": {"old_key_id": str(old.id), "new_key_id": str(new_key.id), "new_key": full_key},
        "message": "Key rotated",
    }