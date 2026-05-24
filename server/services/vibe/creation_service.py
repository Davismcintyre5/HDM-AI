# ====================================================================================================
# server/services/vibe/creation_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
import json

class VibeCreationService:
    async def hashtags(self, content: str, count: int = 10) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Generate {count} relevant hashtags for: {content}. Return JSON: {{\"hashtags\": []}}"}], max_tokens=200)
        try:
            return {"hashtags": json.loads(result.get("reply", "{}")).get("hashtags", [])}
        except:
            return {"hashtags": []}

    async def caption(self, image_description: str, tone: str = "engaging", platform: str = "instagram") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Write a {tone} caption for {platform} about: {image_description}"}], max_tokens=300)
        return {"caption": result.get("reply", "")}

    async def description(self, title: str, content_type: str, length: str = "medium") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Write a {length} description for a {content_type} titled '{title}'"}], max_tokens=400)
        return {"description": result.get("reply", "")}

    async def thumbnail_suggestions(self, title: str, style: str = "modern") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Suggest thumbnail ideas for '{title}' in {style} style. Return JSON: {{\"suggestions\": []}}"}], max_tokens=300)
        try:
            return {"suggestions": json.loads(result.get("reply", "{}")).get("suggestions", [])}
        except:
            return {"suggestions": []}

vibe_creation_service = VibeCreationService()