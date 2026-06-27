# ====================================================================================================
# HDM AI Engine - External API Service
# MERN provides decrypted keys — Python just makes the call
# ====================================================================================================

import httpx
import time
from typing import Dict, Any, Optional
from loguru import logger


class ExternalService:

    async def call_external_api(
        self,
        api_key: str,
        base_url: str,
        method: str = "GET",
        endpoint: str = "/",
        body: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Call external API using key provided by MERN."""

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
                except Exception:
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
        self, api_key: str, base_url: str, endpoint: str
    ) -> Dict[str, Any]:
        """Fetch data for AI analysis. MERN provides the key."""
        result = await self.call_external_api(api_key, base_url, "GET", endpoint)
        if result.get("success"):
            logger.info(f"Data fetched: {endpoint}")
        return result


external_service = ExternalService()