from typing import Dict, Any
from services.ai_service import ai_service
import json

class VibeAccessibilityService:
    async def alt_text(self, image_url: str, description: str = None, data: dict = None) -> Dict[str, Any]:
        prompt = f"Generate alt text for image: {image_url}"
        if description: prompt += f" Description: {description}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=150, module="vibe")
        return {"alt_text": result.get("reply", "")}

    async def captions(self, video_url: str, language: str = "en", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Generate captions in {language} for video: {video_url}"}], max_tokens=300, module="vibe")
        return {"captions": result.get("reply", "")}

    async def text_to_speech(self, text: str, voice: str = "default", language: str = "en", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Convert to speech in {language}: {text[:500]}. Return JSON: {{\"audio_url\": \"...\"}}"}], max_tokens=100, module="vibe")
        try: return {"audio_url": json.loads(result.get("reply", "{}")).get("audio_url", "")}
        except: return {"audio_url": ""}

vibe_accessibility_service = VibeAccessibilityService()