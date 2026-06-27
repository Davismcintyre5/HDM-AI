# ====================================================================================================
# 35. server/services/general/image_service.py
# ====================================================================================================
from typing import Dict, Any, List, Optional
from loguru import logger
from services.ai_service import ai_service

class ImageService:
    VALID_STYLES = ["realistic", "cartoon", "anime", "oil-painting", "watercolor", "sketch", "3d-render", "pixel-art"]

    async def generate(self, user_id: str, prompt: str, style: str = "realistic", size: str = "1024x1024", num_images: int = 1) -> Dict[str, Any]:
        if style not in self.VALID_STYLES: return {"success": False, "error": f"Invalid style. Choose from: {', '.join(self.VALID_STYLES)}"}
        enhanced_prompt = self._enhance_prompt(prompt, style)
        logger.info(f"Image description: style={style}, prompt='{prompt[:80]}...'")
        descriptions = []
        for i in range(max(1, min(num_images, 4))):
            result = await ai_service.gemini_image(enhanced_prompt)
            if result.get("success"): descriptions.append({"description": result.get("description", ""), "prompt": enhanced_prompt, "note": result.get("note", "")})
            else: logger.error(f"Description failed: {result.get('error')}")
        if not descriptions: return {"success": False, "error": "Failed to generate descriptions"}
        return {"success": True, "images": descriptions, "revised_prompt": enhanced_prompt, "style": style, "count": len(descriptions), "note": descriptions[0].get("note", "")}

    async def analyze_image(self, image_base64: str, prompt: str = "Describe this image in detail.") -> Dict[str, Any]:
        result = await ai_service.gemini_vision(prompt=prompt, image_base64=image_base64)
        return {"success": True, "analysis": result.get("analysis", "")} if result.get("success") else {"success": False, "error": result.get("error", "Analysis failed")}

    async def generate_variations(self, image_base64: str, num_variations: int = 2) -> Dict[str, Any]:
        analysis = await self.analyze_image(image_base64, "Describe this image in one detailed paragraph for image regeneration.")
        if not analysis.get("success"): return analysis
        return await self.generate(user_id="system", prompt=analysis["analysis"], style="realistic", num_images=num_variations)

    def _enhance_prompt(self, prompt: str, style: str) -> str:
        style_prompts = {"realistic": "photorealistic, highly detailed", "cartoon": "cartoon style, vibrant colors", "anime": "anime style, Japanese animation", "oil-painting": "oil painting style, textured", "watercolor": "watercolor painting, soft edges", "sketch": "pencil sketch, detailed linework", "3d-render": "3D render, octane render", "pixel-art": "pixel art, 8-bit, retro"}
        return f"{prompt}, {style_prompts.get(style, 'realistic')}"

image_service = ImageService()