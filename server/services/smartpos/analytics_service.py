# ====================================================================================================
# 8. server/services/smartpos/analytics_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.smartpos.analytics_cache import AnalyticsCache
from datetime import datetime, timedelta
from loguru import logger
import json

class AnalyticsService:
    async def analyze(self, business_id: str, analytics_type: str, period: str = "this_month", data: dict = None, filters: dict = None) -> Dict[str, Any]:
        if not data:
            return {"type": analytics_type, "data": {}, "summary": "No data provided. Send real data for analysis.", "error": "no_data"}

        cached = await AnalyticsCache.find_one(AnalyticsCache.business_id == business_id, AnalyticsCache.cache_type == analytics_type)
        if cached and cached.expires_at and cached.expires_at > datetime.utcnow():
            return {"type": analytics_type, "data": cached.data, "summary": "Cached result"}

        parts = [f"You are a POS analytics AI. Analyze this REAL {analytics_type} data for period: {period}.", "", "--- REAL BUSINESS DATA ---"]
        if "summary" in data:
            parts.append(f"\nQUICK SUMMARY:")
            for key, value in data["summary"].items(): parts.append(f"  {key}: {value}")
        if "total_sales" in data:
            parts.append(f"\nTotal Sales: {data['total_sales']}"); parts.append(f"Transactions: {data.get('transactions', '?')}")
        if "top_products" in data:
            parts.append(f"\nTOP PRODUCTS:")
            for p in data["top_products"][:10]: parts.append(f"  • {p.get('name','?')}: Sales {p.get('sales',0)}, Qty {p.get('quantity',0)}")
        if "daily_breakdown" in data:
            parts.append(f"\nDAILY BREAKDOWN:")
            for d in data["daily_breakdown"][:7]: parts.append(f"  • {d.get('date','?')}: {d.get('sales',0)}")
        parts.append("\n\nReturn JSON: {\"data\": {...}, \"summary\": \"key findings from real data\", \"recommendations\": []}")
        parts.append("⚠️ Use ONLY the real data above. Reference specific numbers and product names.")

        prompt = "\n".join(parts)
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=800, service="smartpos")
        try:
            parsed = json.loads(result.get("reply", "{}"))
            cache = AnalyticsCache(business_id=business_id, cache_type=analytics_type, data=parsed.get("data", {}), expires_at=datetime.utcnow() + timedelta(hours=1))
            await cache.insert()
            return {"type": analytics_type, "data": parsed.get("data", {}), "summary": parsed.get("summary", ""), "recommendations": parsed.get("recommendations", [])}
        except:
            return {"type": analytics_type, "data": data, "summary": "Could not analyze data."}

analytics_service = AnalyticsService()