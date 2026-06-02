# ====================================================================================================
# 25. server/services/vibe/moderation_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.vibe.moderation_log import ModerationLog
import json

class VibeModerationService:
    async def moderate_text(self, text: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Moderate this text. Return JSON: {{\"flagged\": true/false, \"category\": \"spam/hate_speech/nsfw/clean\", \"confidence\": 0.0-1.0, \"reason\": \"...\"}}.\nText: {text}"}], temperature=0.1, max_tokens=150, service="vibe")
        try:
            d = json.loads(result.get("reply", "{}"))
            await ModerationLog(content_id="txt", content_type="text", flagged=d.get("flagged", False), category=d.get("category", ""), confidence=d.get("confidence", 0), action="flagged" if d.get("flagged") else "allowed").insert()
            return d
        except: return {"flagged": False, "category": "clean", "reason": "Could not analyze"}

    async def moderate_image(self, image_url: str, description: str = None, data: dict = None) -> Dict[str, Any]:
        prompt = f"Moderate this image: {image_url}"
        if description: prompt += f" — {description}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt + " Return JSON: {\"flagged\": true/false, \"category\": \"...\"}"}], temperature=0.1, max_tokens=150, service="vibe")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"flagged": False}

    async def moderate_video(self, video_url: str, description: str = None, data: dict = None) -> Dict[str, Any]:
        prompt = f"Moderate this video: {video_url}"
        if description: prompt += f" — {description}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt + " Return JSON: {\"flagged\": true/false}"}], temperature=0.1, max_tokens=150, service="vibe")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"flagged": False}

    async def moderate_comment(self, comment: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Is this comment appropriate? Return JSON: {{\"flagged\": true/false}}.\nComment: {comment}"}], max_tokens=100, service="vibe")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"flagged": False}

    async def moderate_batch(self, items: list, data: dict = None) -> Dict[str, Any]:
        results = []
        for item in items[:10]:
            if isinstance(item, str): results.append(await self.moderate_text(item))
        return {"results": results}

vibe_moderation_service = VibeModerationService()