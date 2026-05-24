# ====================================================================================================
# server/services/vibe/accessibility_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.vibe.accessibility_cache import AccessibilityCache

class VibeAccessibilityService:
    async def alt_text(self, image_url: str, description: str = None) -> Dict[str, Any]:
        prompt = f"Generate alt text for image: {image_url}"
        if description: prompt += f" Description: {description}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=150)
        text = result.get("reply", "")
        await AccessibilityCache(content_id=image_url, alt_text=text).insert()
        return {"alt_text": text}

    async def captions(self, video_url: str, language: str = "en") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Generate captions in {language} for video: {video_url}"}], max_tokens=300)
        captions = result.get("reply", "")
        await AccessibilityCache(content_id=video_url, captions=captions).insert()
        return {"captions": captions}

    async def text_to_speech(self, text: str, voice: str = "default", language: str = "en") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Convert to speech in {language}: {text}. Return JSON: {{\"audio_url\": \"...\"}}"}], max_tokens=100)
        try:
            import json
            data = json.loads(result.get("reply", "{}"))
            await AccessibilityCache(content_id=text[:50], audio_url=data.get("audio_url", "")).insert()
            return {"audio_url": data.get("audio_url", "")}
        except:
            return {"audio_url": ""}

vibe_accessibility_service = VibeAccessibilityService()