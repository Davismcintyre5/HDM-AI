# ====================================================================================================
# server/services/vibe/search_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
import json

class VibeSearchService:
    async def semantic_search(self, query: str, limit: int = 20) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Semantic search for: {query}. Return top {limit} results as JSON: {{\"results\": []}}"}], max_tokens=500)
        try:
            return {"results": json.loads(result.get("reply", "{}")).get("results", [])}
        except:
            return {"results": []}

    async def visual_search(self, image_url: str, limit: int = 10) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Visual search for image: {image_url}. Return similar items as JSON: {{\"results\": []}}"}], max_tokens=300)
        try:
            return {"results": json.loads(result.get("reply", "{}")).get("results", [])}
        except:
            return {"results": []}

    async def voice_search(self, audio_url: str, language: str = "en") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Process voice search from {audio_url} in {language}. Return JSON: {{\"results\": []}}"}], max_tokens=300)
        try:
            return {"results": json.loads(result.get("reply", "{}")).get("results", [])}
        except:
            return {"results": []}

vibe_search_service = VibeSearchService()