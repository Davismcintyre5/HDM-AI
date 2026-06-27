# ====================================================================================================
# HDM AI Engine - services/key_resolver.py
# Fetches AI keys from MERN | Falls back to .env | Optional Redis cache
# ====================================================================================================

import os
import httpx
from typing import Dict
from loguru import logger
from config import settings


class KeyResolver:
    """Resolves AI provider keys per module. MERN first, .env fallback."""

    def __init__(self):
        self.cache: Dict[str, dict] = {}
        self.mern_url = settings.MERN_INTERNAL_URL
        self.internal_secret = settings.MERN_INTERNAL_SECRET
        self._redis = None

        self.fallback_keys = {
            "general_groq": settings.GROQ_API_KEY,
            "erp_groq": settings.GROQ_API_KEY_ERP,
            "smartpos_groq": settings.GROQ_API_KEY_SMARTPOS,
            "spark_groq": settings.GROQ_API_KEY_SPARK,
            "vibe_groq": settings.GROQ_API_KEY_SPARK,
            "vault_groq": settings.GROQ_API_KEY_SPARK,
            "widget_groq": settings.GROQ_API_KEY_SPARK,
            "general_gemini": settings.GEMINI_API_KEY,
            "erp_gemini": settings.GEMINI_API_KEY,
            "smartpos_gemini": settings.GEMINI_API_KEY,
            "spark_gemini": settings.GEMINI_API_KEY,
            "vibe_gemini": settings.GEMINI_API_KEY,
            "vault_gemini": settings.GEMINI_API_KEY,
            "widget_gemini": settings.GEMINI_API_KEY,
        }

        self.default_models = {
            "groq": "llama-3.3-70b-versatile",
            "gemini": "gemini-2.5-flash",
        }

    async def _init_redis(self):
        if not settings.REDIS_ENABLED:
            return
        if self._redis is not None:
            return
        try:
            import redis.asyncio as redis
            self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await self._redis.ping()
            logger.info("KeyResolver: Redis connected")
        except Exception as e:
            logger.warning(f"KeyResolver: Redis unavailable — {e}")
            self._redis = None

    async def fetch_from_mern(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(
                    f"{self.mern_url}/api/v1/internal/keys",
                    headers={"X-Internal-Secret": self.internal_secret},
                )
                if resp.status_code == 200:
                    mern_keys = resp.json().get("keys", [])
                    for entry in mern_keys:
                        module = entry["module"]
                        provider = entry["provider"]
                        cache_key = f"{module}_{provider}"
                        self.cache[cache_key] = {
                            "key": entry["apiKey"],
                            "model": entry.get("model", self.default_models.get(provider, "")),
                            "is_active": entry.get("isActive", True),
                        }
                    logger.info(f"KeyResolver: Loaded {len(mern_keys)} keys from MERN")
                    return True
                else:
                    logger.warning(f"KeyResolver: MERN returned {resp.status_code}")
                    return False
        except Exception as e:
            logger.warning(f"KeyResolver: MERN unreachable — {e}")
            return False

    async def resolve(self, module: str, provider: str) -> dict:
        cache_key = f"{module}_{provider}"

        if cache_key in self.cache and self.cache[cache_key].get("is_active"):
            return self.cache[cache_key]

        if settings.REDIS_ENABLED:
            await self._init_redis()
            if self._redis:
                try:
                    import json
                    cached = await self._redis.get(f"ai_key:{cache_key}")
                    if cached:
                        data = json.loads(cached)
                        self.cache[cache_key] = data
                        return data
                except Exception:
                    pass

        success = await self.fetch_from_mern()
        if success and cache_key in self.cache:
            if settings.REDIS_ENABLED and self._redis:
                try:
                    import json
                    await self._redis.set(f"ai_key:{cache_key}", json.dumps(self.cache[cache_key]), ex=300)
                except Exception:
                    pass
            return self.cache[cache_key]

        fallback = self.fallback_keys.get(cache_key, "")
        if fallback:
            logger.warning(f"KeyResolver: Using .env fallback for {cache_key}")
            return {"key": fallback, "model": self.default_models.get(provider, ""), "is_active": True}

        logger.error(f"KeyResolver: No key found for {cache_key}")
        return {"key": "", "model": "", "is_active": False}


key_resolver = KeyResolver()