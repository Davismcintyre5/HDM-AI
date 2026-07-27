from services.ai_service import ai_service
import json

class TrendingService:
    async def detect(self, posts: list) -> dict:
        posts_text = "\n".join([p.get("content", "") for p in posts[:50]])
        prompt = f"""Detect trending topics from these recent posts. Return top 5.
Posts:
{posts_text}

Return JSON: {{"topics": [{{"keyword": "...", "category": "sports/academic/social/events/other", "score": 0.0-1.0, "postCount": 0, "momentum": "rising/peak/declining"}}]}}"""

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=400, module="rvnp")
        try:
            return json.loads(result.get("reply", "{}"))
        except:
            return {"topics": []}

trending_service = TrendingService()