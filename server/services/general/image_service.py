# ====================================================================================================
# server/services/general/image_service.py
# ====================================================================================================
"""
HDM AI - Image Generation Service
Uses Gemini for rich text descriptions (free tier)
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from services.ai_service import ai_service


class ImageService:
    """AI image description service."""

    VALID_STYLES = [
        "realistic", "cartoon", "anime", "oil-painting",
        "watercolor", "sketch", "3d-render", "pixel-art",
    ]
    VALID_SIZES = ["512x512", "1024x1024", "1792x1024", "1024x1792"]

    async def generate(
        self,
        user_id: str,
        prompt: str,
        style: str = "realistic",
        size: str = "1024x1024",
        num_images: int = 1,
    ) -> Dict[str, Any]:
        """Generate image descriptions via Gemini."""

        if style not in self.VALID_STYLES:
            return {
                "success": False,
                "error": f"Invalid style. Choose from: {', '.join(self.VALID_STYLES)}",
            }

        num_images = max(1, min(num_images, 4))
        enhanced_prompt = self._enhance_prompt(prompt, style)

        logger.info(f"Image description: style={style}, prompt='{prompt[:80]}...'")

        descriptions = []
        for i in range(num_images):
            result = await ai_service.gemini_image(enhanced_prompt)
            if result.get("success"):
                descriptions.append({
                    "description": result.get("description", ""),
                    "prompt": enhanced_prompt,
                    "note": result.get("note", ""),
                })
            else:
                logger.error(f"Description failed: {result.get('error')}")

        if not descriptions:
            return {"success": False, "error": "Failed to generate descriptions"}

        return {
            "success": True,
            "images": descriptions,
            "revised_prompt": enhanced_prompt,
            "style": style,
            "count": len(descriptions),
            "note": descriptions[0].get("note", ""),
        }

    async def analyze_image(
        self,
        image_base64: str,
        prompt: str = "Describe this image in detail.",
    ) -> Dict[str, Any]:
        """Analyze an image via Gemini Vision."""
        result = await ai_service.gemini_vision(
            prompt=prompt,
            image_base64=image_base64,
        )
        if result.get("success"):
            return {"success": True, "analysis": result["analysis"]}
        return {"success": False, "error": result.get("error", "Analysis failed")}

    async def generate_variations(
        self,
        image_base64: str,
        num_variations: int = 2,
    ) -> Dict[str, Any]:
        """Generate variations of an image."""
        analysis = await self.analyze_image(
            image_base64,
            "Describe this image in one detailed paragraph for image regeneration.",
        )
        if not analysis.get("success"):
            return analysis

        return await self.generate(
            user_id="system",
            prompt=analysis["analysis"],
            style="realistic",
            num_images=num_variations,
        )

    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt with style keywords."""
        style_prompts = {
            "realistic": "photorealistic, highly detailed, 8k resolution, professional photography",
            "cartoon": "cartoon style, vibrant colors, clean lines, animated",
            "anime": "anime style, Japanese animation, detailed, vibrant",
            "oil-painting": "oil painting style, textured brushstrokes, fine art, gallery quality",
            "watercolor": "watercolor painting, soft edges, artistic, flowing colors",
            "sketch": "pencil sketch, hand-drawn, detailed linework, black and white",
            "3d-render": "3D render, octane render, unreal engine, photorealistic CGI",
            "pixel-art": "pixel art, 8-bit, retro game style, blocky, nostalgic",
        }
        style_desc = style_prompts.get(style, style_prompts["realistic"])
        return f"{prompt}, {style_desc}"


image_service = ImageService()