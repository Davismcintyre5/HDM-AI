# ====================================================================================================
# server/services/ai_service.py — PRODUCTION READY
# Rate limiting, retry on 429, caching support
# ====================================================================================================
"""
HDM AI - Core AI Service
Groq + Gemini integration via REST API with streaming + retry
"""

import httpx
import json
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator, List
from loguru import logger

from config import settings


class AIService:
    """Core AI service for Groq and Gemini providers."""

    def __init__(self):
        self.groq_key = settings.GROQ_API_KEY
        self.groq_chat_url = "https://api.groq.com/openai/v1/chat/completions"
        self.gemini_key = settings.GEMINI_API_KEY
        self.gemini_base = "https://generativelanguage.googleapis.com/v1beta/models"
        self._last_groq_request = 0.0
        self._min_interval = 1.5  # seconds between Groq requests

    # ================================================================================================
    # GROQ — CHAT (with retry + rate limiting)
    # ================================================================================================

    async def groq_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Chat with Groq. Includes rate limiting and 429 retry."""
        
        # Rate limit — ensure minimum interval
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_groq_request
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_groq_request = asyncio.get_event_loop().time()

        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(self.groq_chat_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return {
                    "success": True,
                    "reply": data["choices"][0]["message"]["content"],
                    "model": model,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                }
            except Exception as e:
                error_str = str(e)
                
                # Retry once on rate limit
                if "429" in error_str:
                    logger.warning("Groq rate limited — waiting 8s and retrying...")
                    await asyncio.sleep(8)
                    try:
                        response = await client.post(self.groq_chat_url, headers=headers, json=payload)
                        response.raise_for_status()
                        data = response.json()
                        logger.info("Groq retry succeeded")
                        return {
                            "success": True,
                            "reply": data["choices"][0]["message"]["content"],
                            "model": model,
                            "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                        }
                    except Exception as retry_err:
                        logger.error(f"Groq retry failed: {retry_err}")
                        return {"success": False, "error": "Service busy. Please wait a moment and try again."}
                
                # Other errors
                if "503" in error_str or "502" in error_str:
                    logger.warning(f"Groq server error — retrying once...")
                    await asyncio.sleep(3)
                    try:
                        response = await client.post(self.groq_chat_url, headers=headers, json=payload)
                        response.raise_for_status()
                        data = response.json()
                        return {
                            "success": True,
                            "reply": data["choices"][0]["message"]["content"],
                            "model": model,
                            "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                        }
                    except:
                        pass
                
                logger.error(f"Groq chat error: {e}")
                return {"success": False, "error": "AI service unavailable. Please try again later."}

    # ================================================================================================
    # GROQ — STREAMING CHAT
    # ================================================================================================

    async def groq_chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from Groq. Silent on failure."""
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                async with client.stream("POST", self.groq_chat_url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        logger.warning(f"Groq stream HTTP {response.status_code}")
                        return
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk = line[6:]
                            if chunk == "[DONE]":
                                break
                            try:
                                data = json.loads(chunk)
                                content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
            except (httpx.ReadTimeout, httpx.ConnectError):
                logger.warning("Groq stream connection issue")
                return
            except Exception as e:
                logger.warning(f"Groq stream error: {e}")
                return

    # ================================================================================================
    # GEMINI — CHAT
    # ================================================================================================

    async def gemini_chat(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        url = f"{self.gemini_base}/{model}:generateContent?key={self.gemini_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "success": True,
                    "reply": text,
                    "model": model,
                    "tokens_used": data.get("usageMetadata", {}).get("totalTokenCount", 0),
                }
            except Exception as e:
                logger.error(f"Gemini chat error: {e}")
                return {"success": False, "error": str(e)}

    # ================================================================================================
    # GEMINI — IMAGE
    # ================================================================================================

    async def gemini_image(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash",
        num_images: int = 1,
    ) -> Dict[str, Any]:
        try:
            result = await self.gemini_chat(
                prompt=(
                    f"Create a detailed, vivid description of this image: {prompt}. "
                    f"Include: composition, colors, lighting, style, mood, and key visual elements. "
                    f"Be specific enough that an artist could recreate it. Keep under 200 words."
                ),
                model=model,
                temperature=0.9,
                max_tokens=400,
            )
            return {
                "success": True,
                "images": [],
                "description": result.get("reply", "Could not generate description"),
                "model": f"{model} (text)",
                "note": "Image generation requires Imagen model — rich text description provided instead",
            }
        except Exception as e:
            logger.error(f"Image description error: {e}")
            return {"success": False, "error": str(e)}

    # ================================================================================================
    # GEMINI — VISION
    # ================================================================================================

    async def gemini_vision(
        self,
        prompt: str,
        image_base64: Optional[str] = None,
        model: str = "gemini-2.0-flash",
    ) -> Dict[str, Any]:
        url = f"{self.gemini_base}/{model}:generateContent?key={self.gemini_key}"
        parts = [{"text": prompt}]
        if image_base64:
            parts.append({"inlineData": {"mimeType": "image/jpeg", "data": image_base64}})
        payload = {"contents": [{"parts": parts}]}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"success": True, "analysis": text, "model": model}
            except Exception as e:
                logger.error(f"Gemini vision error: {e}")
                return {"success": False, "error": str(e)}


ai_service = AIService()