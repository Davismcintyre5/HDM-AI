# ====================================================================================================
# server/services/smartpos/search_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from loguru import logger

class SearchService:
    async def search(self, business_id: str, query: str, limit: int = 10) -> Dict[str, Any]:
        prompt = f"""You are a POS search AI. Find results for: "{query}". Return {limit} items.
Return JSON: {{"results": [{{"title": "...", "description": "..."}}]}}"""
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=500)
        try:
            import json
            data = json.loads(result.get("reply", "{}"))
            return {"results": data.get("results", [])}
        except:
            return {"results": []}

search_service = SearchService()