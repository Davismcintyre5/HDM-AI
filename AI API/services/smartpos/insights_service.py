from typing import Dict, Any
from services.ai_service import ai_service
import json

class InsightsService:
    async def get_insights(self, business_id: str, insight_type: str, data: dict = None) -> Dict[str, Any]:
        if not data:
            return {"type": insight_type, "data": {}, "summary": "No financial data provided."}

        parts = [f"You are a POS insights AI. Analyze this REAL financial data for {insight_type} insights.", "", "--- REAL FINANCIAL DATA ---"]
        if "revenue" in data: parts.append(f"\nRevenue: {data['revenue']}")
        if "expenses" in data: parts.append(f"Expenses: {data['expenses']}")
        if "profit" in data: parts.append(f"Profit: {data['profit']}")
        if "transactions" in data:
            parts.append(f"\nTRANSACTIONS ({len(data['transactions'])} records):")
            for t in data["transactions"][:10]: parts.append(f"  • {t.get('date','?')}: {t.get('description','?')} — {t.get('amount',0)}")
        parts.append("\n\nReturn JSON: {\"data\": {...}, \"summary\": \"specific insights from real data\", \"recommendations\": []}")

        prompt = "\n".join(parts)
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=600, module="smartpos")
        try:
            parsed = json.loads(result.get("reply", "{}"))
            return {"type": insight_type, "data": parsed.get("data", {}), "summary": parsed.get("summary", ""), "recommendations": parsed.get("recommendations", [])}
        except:
            return {"type": insight_type, "data": {}, "summary": "Could not generate insights."}

insights_service = InsightsService()