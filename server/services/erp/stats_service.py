# ====================================================================================================
# server/services/erp/stats_service.py
# ====================================================================================================
"""
HDM AI - ERP Stats Service
Real-time usage statistics from database
"""

from typing import Dict, Any
from models.erp.usage_log import ERPUsageLog
from models.erp.file_extraction import FileExtraction
from models.erp.alert_schedule import AlertSchedule
from loguru import logger


class ERPStatsService:
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get real ERP usage statistics from the database.
        No AI generation — pure data aggregation.
        """
        
        # Count records
        total_queries = await ERPUsageLog.count()
        total_files = await FileExtraction.count()
        total_alerts = await AlertSchedule.count()
        
        # Get unique tenants
        tenants = set()
        async for log in ERPUsageLog.find_all():
            if log.tenant_id:
                tenants.add(log.tenant_id)
        
        # Calculate total tokens
        total_tokens = 0
        async for log in ERPUsageLog.find_all():
            total_tokens += log.tokens_used or 0
        
        # Get recent queries (last 10)
        recent_queries = []
        async for log in ERPUsageLog.find_all().sort("-timestamp").limit(10):
            recent_queries.append({
                "tenant_id": log.tenant_id,
                "endpoint": log.endpoint,
                "tokens_used": log.tokens_used,
                "status": log.status,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            })
        
        # Provider breakdown
        groq_count = await ERPUsageLog.find(ERPUsageLog.provider == "groq").count()
        gemini_count = await ERPUsageLog.find(ERPUsageLog.provider == "gemini").count()
        
        # Success rate
        success_count = await ERPUsageLog.find(ERPUsageLog.status == "success").count()
        success_rate = round((success_count / total_queries) * 100, 1) if total_queries > 0 else 100
        
        logger.info(f"ERP stats: {total_queries} queries, {len(tenants)} tenants, {total_tokens} tokens")
        
        return {
            "total_requests": total_queries,
            "total_tokens_used": total_tokens,
            "total_files_processed": total_files,
            "total_alerts_generated": total_alerts,
            "unique_tenants": len(tenants),
            "tenants": list(tenants),
            "success_rate": success_rate,
            "providers": {
                "groq": groq_count,
                "gemini": gemini_count,
            },
            "recent_queries": recent_queries,
        }


erp_stats_service = ERPStatsService()