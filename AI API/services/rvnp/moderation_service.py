from services.ai_service import ai_service
import json

class ModerationService:
    async def moderate(self, text: str = None, imageUrl: str = None) -> dict:
        if not text and not imageUrl:
            return {"flagged": False, "reason": None, "confidence": 0, "categories": {}}

        prompt = """Analyze this content for: hate_speech, nsfw, spam, violence, harassment, inappropriate.
Return ONLY a JSON object. No markdown, no explanation. Just the JSON.
Format: {"flagged": true/false, "reason": "hate_speech/nsfw/spam/violence/harassment/inappropriate or null", "confidence": 0.0-1.0, "categories": {"hate_speech": 0.0, "nsfw": 0.0, "spam": 0.0, "violence": 0.0, "harassment": 0.0, "inappropriate": 0.0}}

"""
        if text:
            prompt += f"Text: {text}\n"
        if imageUrl:
            prompt += f"Image URL: {imageUrl}\n"

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=300, module="rvnp")

        try:
            reply = result.get("reply", "{}")
            reply = reply.replace("```json", "").replace("```", "").strip()
            return json.loads(reply)
        except:
            return {"flagged": False, "reason": None, "confidence": 0, "categories": {}}

moderation_service = ModerationService()