"""
HDM AI - External API Service
Calls external systems using stored inbound keys
"""

import httpx
import time
from typing import Dict, Any, Optional
from loguru import logger

from models.core import ThirdPartyKey
from utils.encryption import decrypt_key

KNOWN_URLS = {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "google": "https://generativelanguage.googleapis.com/v1beta",
}


class ExternalService:

    async def call_external_api(
        self,
        user_id: str,
        provider: str,
        method: str = "GET",
        endpoint: str = "/",
        body: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Call external API using stored key."""

        key = await ThirdPartyKey.find_one(
            ThirdPartyKey.user_id == user_id,
            ThirdPartyKey.provider == provider,
            ThirdPartyKey.is_active == True,
        )
        if not key:
            return {"success": False, "error": f"No active key for {provider}"}

        api_key = decrypt_key(key.encrypted_key)
        base_url = key.base_url or KNOWN_URLS.get(provider, "")
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                if method.upper() == "GET":
                    resp = await client.get(url, headers=headers)
                elif method.upper() == "POST":
                    resp = await client.post(url, headers=headers, json=body or {})
                elif method.upper() == "PUT":
                    resp = await client.put(url, headers=headers, json=body or {})
                elif method.upper() == "DELETE":
                    resp = await client.delete(url, headers=headers)
                else:
                    return {"success": False, "error": f"Unsupported method: {method}"}

                elapsed = (time.time() - start) * 1000

                try:
                    data = resp.json()
                except:
                    data = resp.text

                return {
                    "success": resp.status_code < 400,
                    "status_code": resp.status_code,
                    "data": data,
                    "response_time_ms": round(elapsed, 2),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def fetch_data_for_analysis(
        self, user_id: str, provider: str, endpoint: str
    ) -> Dict[str, Any]:
        """Fetch data for AI analysis."""
        result = await self.call_external_api(user_id, provider, "GET", endpoint)
        if result.get("success"):
            logger.info(f"Data fetched: {provider}{endpoint}")
        return result


external_service = ExternalService()