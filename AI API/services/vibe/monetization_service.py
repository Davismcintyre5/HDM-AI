from typing import Dict, Any
from services.ai_service import ai_service
import json

class VibeMonetizationService:
    async def ad_target(self, campaign_goal: str, budget: float = None, audience: dict = None, data: dict = None) -> Dict[str, Any]:
        prompt = f"Suggest ad targeting for: {campaign_goal}. Return JSON: {{\"audience\": []}}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=300, module="vibe")
        try: return {"audience": json.loads(result.get("reply", "{}")).get("audience", [])}
        except: return {"audience": []}

    async def ad_copy(self, product: str, target_audience: str, platform: str = "instagram", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Write ad copy for {product} targeting {target_audience} on {platform}"}], max_tokens=300, module="vibe")
        return {"copy": result.get("reply", "")}

    async def price_suggest(self, product: str, category: str, market_data: dict = None, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Suggest pricing for {product} in {category}. Return JSON: {{\"price\": 0}}"}], max_tokens=150, module="vibe")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"price": 0}

    async def sponsor_match(self, creator_profile: dict, niche: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Match sponsors for {niche} creator. Return JSON: {{\"matches\": []}}"}], max_tokens=300, module="vibe")
        try: return {"matches": json.loads(result.get("reply", "{}")).get("matches", [])}
        except: return {"matches": []}

vibe_monetization_service = VibeMonetizationService()