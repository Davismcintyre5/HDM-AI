# ====================================================================================================
# server/services/smartpos/analytics_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.smartpos.analytics_cache import AnalyticsCache
from datetime import datetime, timedelta
from loguru import logger
import json

class AnalyticsService:
    async def analyze(self, business_id: str, analytics_type: str, period: str = "this_month", data: dict = None, filters: dict = None) -> Dict[str, Any]:
        if data:
            prompt = f"""You are a POS analytics AI. Analyze this REAL business data:

Data: {json.dumps(data)[:3000]}
Analytics type: {analytics_type}
Period: {period}

Provide insights, trends, and recommendations based on the actual data. Return JSON:
{{"data": {{...}}, "summary": "key findings from the real data", "recommendations": []}}"""
        else:
            return {"type": analytics_type, "data": {}, "summary": "No data provided. Send real sales/product data for analysis.", "error": "no_data"}

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=800)
        try:
            parsed = json.loads(result.get("reply", "{}"))
            cache = AnalyticsCache(business_id=business_id, cache_type=analytics_type, data=parsed.get("data", {}), expires_at=datetime.utcnow() + timedelta(hours=1))
            await cache.insert()
            return {"type": analytics_type, "data": parsed.get("data", {}), "summary": parsed.get("summary", ""), "recommendations": parsed.get("recommendations", [])}
        except:
            return {"type": analytics_type, "data": data, "summary": "Could not analyze data."}

analytics_service = AnalyticsService()