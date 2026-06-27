from typing import Dict, Any
from services.ai_service import ai_service
import json

class VibeAnalyticsService:
    async def engagement(self, user_id: str, period: str = "last_30d", data: dict = None) -> Dict[str, Any]:
        context = json.dumps(data)[:2000] if data else ""
        result = await ai_service.groq_chat([{"role": "user", "content": f"Generate engagement metrics for user {user_id} over {period}. Data: {context}\nReturn JSON: {{\"metrics\": {{}}}}"}], max_tokens=400, module="vibe")
        try: return {"metrics": json.loads(result.get("reply", "{}")).get("metrics", {})}
        except: return {"metrics": {}}

    async def churn_prediction(self, user_id: str, activity_data: dict = None, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Predict churn risk for {user_id}. Return JSON: {{\"risk_score\": 0.0-1.0}}"}], max_tokens=200, module="vibe")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"risk_score": 0}

    async def growth_projections(self, user_id: str, metrics: dict = None, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": "Generate growth projections. Return JSON: {\"projections\": {}}"}], max_tokens=300, module="vibe")
        try: return {"projections": json.loads(result.get("reply", "{}")).get("projections", {})}
        except: return {"projections": {}}

vibe_analytics_service = VibeAnalyticsService()