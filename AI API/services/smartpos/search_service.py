from typing import Dict, Any
from services.ai_service import ai_service
import json

class SearchService:
    async def search(self, business_id: str, query: str, limit: int = 10) -> Dict[str, Any]:
        prompt = f"""You are a POS search AI. Find results for: "{query}". Return {limit} items.
Return JSON: {{"results": [{{"title": "...", "description": "..."}}]}}"""
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=500, module="smartpos")
        try:
            return {"results": json.loads(result.get("reply", "{}")).get("results", [])}
        except:
            return {"results": []}

search_service = SearchService()