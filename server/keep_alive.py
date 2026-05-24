# ====================================================================================================
# server/keep_alive.py
# ====================================================================================================
"""
HDM AI - Self-Ping Keep Alive
Prevents Render free tier sleep by pinging own health endpoint every 9 minutes
"""

import httpx
import asyncio
import os
from loguru import logger

SELF_URL = os.getenv("RENDER_EXTERNAL_URL", "https://hdmai-server.onrender.com")
PING_INTERVAL = 540  # 9 minutes (Render sleeps after 15)


async def keep_alive():
    """Ping self health endpoint periodically to prevent sleep."""
    logger.info(f"Keep-alive starting: will ping {SELF_URL}/health every {PING_INTERVAL}s")
    await asyncio.sleep(60)  # Wait for server to fully start

    while True:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{SELF_URL}/health")
                if response.status_code == 200:
                    logger.info("Keep-alive: OK")
                else:
                    logger.warning(f"Keep-alive: HTTP {response.status_code}")
        except Exception as e:
            logger.warning(f"Keep-alive ping failed: {e}")

        await asyncio.sleep(PING_INTERVAL)


if __name__ == "__main__":
    asyncio.run(keep_alive())