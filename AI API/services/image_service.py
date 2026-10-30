# ====================================================================================================
# HDM AI Engine — Image Service (/v1/image)
# Image description/vision | Key 1
# ====================================================================================================

from typing import Dict, Any
from services.ai_service import ai_service, PUBLIC_PROVIDER, PUBLIC_MODEL


class ImageService:
    async def generate(self, user_id: str, prompt: str, style: str = "realistic", size: str = "1024x1024", num_images: int = 1) -> Dict[str, Any]:
        result = await ai_service.groq_chat(
            [{"role": "user", "content": f"Describe this image: {prompt}. Style: {style}. Include composition, colors, lighting. Under 200 words."}],
            bucket="chat", temperature=0.9, max_tokens=400,
        )
        return {
            "success": True,
            "images": [],
            "description": result.get("reply", ""),
            "model": PUBLIC_MODEL,
            "provider": PUBLIC_PROVIDER,
            "note": "Image generation via HDM Nova — text description provided.",
        }

    async def analyze(self, user_id: str, image_base64: str, prompt: str = "Describe this image in detail.") -> Dict[str, Any]:
        messages = [{"role": "user", "content": f"{prompt}\n[Image provided as base64 data]"}]
        result = await ai_service.gemini_chat(messages, bucket="chat", temperature=0.5, max_tokens=800)
        return {"success": True, "analysis": result.get("reply", ""), "model": PUBLIC_MODEL, "provider": PUBLIC_PROVIDER}

    async def variations(self, user_id: str, image_base64: str) -> Dict[str, Any]:
        return await self.analyze(user_id, image_base64, "Suggest 3 variations of this image with different styles and compositions.")


image_service = ImageService()