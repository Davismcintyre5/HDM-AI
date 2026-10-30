# ====================================================================================================
# HDM AI Engine — Key Resolver
# Fetches AI keys from MERN | Falls back to .env | Optional Redis cache
# ====================================================================================================

import httpx
from typing import Dict, List
from loguru import logger
from config import settings


class KeyResolver:
    """Resolves AI provider keys per bucket. MERN first, .env fallback."""

    def __init__(self):
        self.cache: Dict[str, dict] = {}
        self.mern_url = settings.MERN_INTERNAL_URL
        self.internal_secret = settings.MERN_INTERNAL_SECRET
        self._redis = None

        self.fallback_keys = {
            "chat_groq": settings.GROQ_API_KEY,
            "chat_gemini": settings.GEMINI_API_KEY,
            "learn_groq": settings.GROQ_API_KEY_LEARN,
            "completion_groq": settings.GROQ_API_KEY_COMPLETION,
            "completion_groq_backup": settings.GROQ_API_KEY_COMPLETION_BACKUP,
        }

        self.default_models = {
            "groq": "openai/gpt-oss-20b",
            "gemini": "gemini-2.5-flash",
        }

    async def _init_redis(self):
        if not settings.REDIS_ENABLED or self._redis is not None:
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
                    entries = resp.json().get("keys", [])
                    for entry in entries:
                        bucket = entry["module"]
                        provider = entry["provider"]
                        cache_key = f"{bucket}_{provider}"
                        self.cache[cache_key] = {
                            "key": entry["apiKey"],
                            "model": entry.get("model", self.default_models.get(provider, "")),
                            "is_active": entry.get("isActive", True),
                        }
                    logger.info(f"KeyResolver: Loaded {len(entries)} keys from MERN")
                    return True
                logger.warning(f"KeyResolver: MERN returned {resp.status_code}")
                return False
        except Exception as e:
            logger.warning(f"KeyResolver: MERN unreachable — {e}")
            return False

    async def resolve(self, bucket: str, provider: str) -> dict:
        cache_key = f"{bucket}_{provider}"

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

    async def resolve_chain(self, keys: List[tuple]) -> List[dict]:
        """Resolve multiple (bucket, provider) pairs for failover."""
        results = []
        for bucket, provider in keys:
            resolved = await self.resolve(bucket, provider)
            if resolved.get("key"):
                results.append(resolved)
        return results


key_resolver = KeyResolver()