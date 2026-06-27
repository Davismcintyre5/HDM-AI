from typing import Dict, Any, List
from services.ai_service import ai_service
import json

class VibeFeedService:
    async def rank_feed(self, user_id: str, feed_items: List[dict], limit: int = 20, data: dict = None) -> Dict[str, Any]:
        items_json = json.dumps(feed_items)[:3000]
        result = await ai_service.groq_chat([{"role": "user", "content": f"Rank these {len(feed_items)} feed items by relevance. Return top {limit} as JSON: {{\"feed\": []}}\nItems: {items_json}"}], max_tokens=1000, module="vibe")
        try: return {"feed": json.loads(result.get("reply", "{}")).get("feed", feed_items[:limit])}
        except: return {"feed": feed_items[:limit]}

    async def personalize_feed(self, user_id: str, interests: List[str] = None, data: dict = None) -> Dict[str, Any]:
        prompt = f"Suggest personalized content for user with interests: {interests}. Return JSON: {{\"feed\": []}}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=500, module="vibe")
        try: return {"feed": json.loads(result.get("reply", "{}")).get("feed", [])}
        except: return {"feed": []}

    async def trending(self, limit: int = 20, category: str = None, data: dict = None) -> Dict[str, Any]:
        prompt = f"Generate {limit} trending topics"
        if category: prompt += f" in {category}"
        prompt += ". Return JSON: {\"topics\": []}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=500, module="vibe")
        try: return {"topics": json.loads(result.get("reply", "{}")).get("topics", [])}
        except: return {"topics": []}

    async def recommend_users(self, user_id: str, limit: int = 10, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Recommend {limit} users. Return JSON: {{\"users\": []}}"}], max_tokens=300, module="vibe")
        try: return {"users": json.loads(result.get("reply", "{}")).get("users", [])}
        except: return {"users": []}

    async def recommend_content(self, user_id: str, limit: int = 20, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Recommend {limit} content items. Return JSON: {{\"content\": []}}"}], max_tokens=500, module="vibe")
        try: return {"content": json.loads(result.get("reply", "{}")).get("content", [])}
        except: return {"content": []}

vibe_feed_service = VibeFeedService()