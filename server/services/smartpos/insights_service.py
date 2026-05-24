# ====================================================================================================
# server/services/smartpos/insights_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from loguru import logger
import json

class InsightsService:
    async def get_insights(self, business_id: str, insight_type: str, data: dict = None) -> Dict[str, Any]:
        if data:
            prompt = f"""You are a POS insights AI. Analyze this REAL financial data for {insight_type} insights.

Data: {json.dumps(data)[:3000]}

Return JSON: {{"data": {{...}}, "summary": "key insights", "recommendations": []}}"""
        else:
            return {"type": insight_type, "data": {}, "summary": "No financial data provided. Send revenue, expenses, tax data for insights."}

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=600)
        try:
            parsed = json.loads(result.get("reply", "{}"))
            return {"type": insight_type, "data": parsed.get("data", {}), "summary": parsed.get("summary", ""), "recommendations": parsed.get("recommendations", [])}
        except:
            return {"type": insight_type, "data": {}, "summary": "Could not generate insights."}

insights_service = InsightsService()