from typing import Dict, Any

class SystemService:
    async def health(self) -> Dict[str, Any]:
        return {"status": "healthy", "version": "1.0.0"}

    async def stats(self) -> Dict[str, Any]:
        return {"requests_today": 0, "total_requests": 0, "active_users": 0}

system_service = SystemService()