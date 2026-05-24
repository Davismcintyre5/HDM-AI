# ====================================================================================================
# server/services/vibe/moderation_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.vibe.moderation_log import ModerationLog
import json

class VibeModerationService:
    async def moderate_text(self, text: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat([
            {"role": "user", "content": f"Moderate this text. Return JSON: {{\"flagged\": true/false, \"category\": \"spam/hate_speech/nsfw/clean\", \"confidence\": 0.0-1.0, \"reason\": \"...\"}}.\nText: {text}"}
        ], temperature=0.1, max_tokens=150)
        try:
            data = json.loads(result.get("reply", "{}"))
            await ModerationLog(content_id="txt", content_type="text", flagged=data.get("flagged", False), category=data.get("category", ""), confidence=data.get("confidence", 0), action="flagged" if data.get("flagged") else "allowed").insert()
            return data
        except:
            return {"flagged": False, "category": "clean", "reason": "Could not analyze"}

    async def moderate_image(self, image_url: str, description: str = None) -> Dict[str, Any]:
        prompt = f"Moderate this image. URL: {image_url}"
        if description: prompt += f" Description: {description}"
        prompt += " Return JSON: {\"flagged\": true/false, \"category\": \"...\", \"confidence\": 0.0-1.0}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=150)
        try:
            return json.loads(result.get("reply", "{}"))
        except:
            return {"flagged": False}

    async def moderate_video(self, video_url: str, description: str = None) -> Dict[str, Any]:
        prompt = f"Moderate this video. URL: {video_url}"
        if description: prompt += f" Description: {description}"
        prompt += " Return JSON: {\"flagged\": true/false, \"category\": \"...\"}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=150)
        try:
            return json.loads(result.get("reply", "{}"))
        except:
            return {"flagged": False}

    async def moderate_comment(self, comment: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Check if this comment is appropriate. Return JSON: {{\"flagged\": true/false, \"reason\": \"...\"}}.\nComment: {comment}"}], max_tokens=100)
        try:
            return json.loads(result.get("reply", "{}"))
        except:
            return {"flagged": False}

    async def moderate_batch(self, items: list) -> Dict[str, Any]:
        results = []
        for item in items[:10]:
            if isinstance(item, str):
                r = await self.moderate_text(item)
                results.append(r)
        return {"results": results}

vibe_moderation_service = VibeModerationService()