# ====================================================================================================
# server/services/erp/stats_service.py
# ====================================================================================================
from typing import Dict, Any
from models.erp.usage_log import ERPUsageLog
from loguru import logger

class ERPStatsService:
    async def get_stats(self) -> Dict[str, Any]:
        total = await ERPUsageLog.count()
        tokens = 0
        tenants = set()
        async for log in ERPUsageLog.find_all():
            tokens += log.tokens_used
            tenants.add(log.tenant_id)
        return {"total_requests": total, "tokens_used": tokens, "tenants": list(tenants)}

erp_stats_service = ERPStatsService()