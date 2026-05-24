# ====================================================================================================
# server/services/spark/system_service.py
# ====================================================================================================
from typing import Dict, Any
from models.spark.moderation_log import ModerationLog
from models.spark.voice_session import VoiceSession

class SystemService:
    async def health(self) -> Dict[str, Any]:
        return {"status": "healthy", "version": "1.0.0"}

    async def stats(self) -> Dict[str, Any]:
        total = await ModerationLog.count()
        return {"requests_today": 0, "total_requests": total, "active_users": 0}

system_service = SystemService()