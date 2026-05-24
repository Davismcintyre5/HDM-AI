# ====================================================================================================
# server/middleware/rate_limit.py
# ====================================================================================================
"""
HDM AI - Rate Limiting Middleware
Per-IP and per-user rate limits using slowapi
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from config import settings

limiter = Limiter(key_func=get_remote_address)


class RateLimitMiddleware:
    """Rate limiting utilities."""

    @staticmethod
    def global_limit():
        """Global rate limit: requests per minute."""
        return limiter.limit(f"{settings.RATE_LIMIT_GLOBAL}/minute")

    @staticmethod
    def per_user_limit():
        """Per-user rate limit: requests per minute."""
        return limiter.limit(f"{settings.RATE_LIMIT_PER_USER}/minute")

    @staticmethod
    def custom_limit(requests_per_minute: int):
        """Custom rate limit."""
        return limiter.limit(f"{requests_per_minute}/minute")