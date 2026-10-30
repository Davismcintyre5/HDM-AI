# ====================================================================================================
# HDM AI Engine — keep_alive.py
# Self-ping to prevent free tier sleep
# ====================================================================================================

import asyncio
import httpx
from loguru import logger
from config import settings


async def keep_alive():
    """Ping own health endpoint every 9 minutes."""
    url = f"{settings.APP_URL}/health"
    while True:
        await asyncio.sleep(540)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    logger.debug("Keep-alive: OK")
        except Exception as e:
            logger.warning(f"Keep-alive failed: {e}")