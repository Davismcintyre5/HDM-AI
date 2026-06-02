# ====================================================================================================
# server/services/ai_service.py — Update key mapping
# ====================================================================================================
"""
HDM AI - Core AI Service
Multi-key Groq + Gemini integration with streaming + retry + usage logging
"""

import httpx
import json
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator, List
from loguru import logger
from config import settings


class AIService:

    def __init__(self):
        self.groq_chat_url = "https://api.groq.com/openai/v1/chat/completions"
        self.gemini_key = settings.GEMINI_API_KEY
        self.gemini_base = "https://generativelanguage.googleapis.com/v1beta/models"
        self.keys = {
            "general": settings.GROQ_API_KEY,
            "widget": settings.GROQ_API_KEY,
            "vault": settings.GROQ_API_KEY,
            "erp": settings.GROQ_API_KEY_ERP,
            "smartpos": settings.GROQ_API_KEY_SMARTPOS,
            "spark": settings.GROQ_API_KEY_SPARK,
            "vibe": settings.GROQ_API_KEY_SPARK,
        }

    def _get_key(self, service: str = "general") -> str:
        return self.keys.get(service, settings.GROQ_API_KEY)

    async def _log_usage(self, service: str, model: str, tokens: int, status: str = "success"):
        try:
            from models.core import UsageLog
            await UsageLog(
                project=service, endpoint="/chat", provider="groq",
                model=model, tokens_used=tokens, status=status,
            ).insert()
        except Exception:
            pass

    async def groq_chat(
        self, messages: List[Dict[str, str]], model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7, max_tokens: int = 1024, timeout: int = 30, service: str = "general",
    ) -> Dict[str, Any]:
        key = self._get_key(service)
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "stream": False}

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(self.groq_chat_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                tokens = data.get("usage", {}).get("total_tokens", 0)
                logger.info(f"Groq[{service}]: {tokens} tokens")
                await self._log_usage(service, model, tokens, "success")
                return {"success": True, "reply": data["choices"][0]["message"]["content"], "model": model, "tokens_used": tokens}
            except Exception as e:
                error_str = str(e)
                logger.error(f"Groq[{service}]: {error_str[:200]}")
                if "429" in error_str:
                    logger.warning(f"Groq[{service}] rate limited — retrying in 10s...")
                    await asyncio.sleep(10)
                    try:
                        response = await client.post(self.groq_chat_url, headers=headers, json=payload)
                        response.raise_for_status()
                        data = response.json()
                        tokens = data.get("usage", {}).get("total_tokens", 0)
                        logger.info(f"Groq[{service}] retry: {tokens} tokens")
                        await self._log_usage(service, model, tokens, "success")
                        return {"success": True, "reply": data["choices"][0]["message"]["content"], "model": model, "tokens_used": tokens}
                    except Exception as retry_err:
                        logger.error(f"Groq[{service}] retry failed: {str(retry_err)[:200]}")
                        await self._log_usage(service, model, 0, "error")
                        return {"success": False, "error": "AI service temporarily unavailable."}
                await self._log_usage(service, model, 0, "error")
                return {"success": False, "error": "AI service unavailable."}

    async def groq_chat_stream(
        self, messages, model="llama-3.3-70b-versatile",
        temperature=0.7, max_tokens=1024, service="general",
    ) -> AsyncGenerator[str, None]:
        key = self._get_key(service)
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages, "stream": True, "temperature": temperature, "max_tokens": max_tokens}
        total_tokens = 0
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                async with client.stream("POST", self.groq_chat_url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        await self._log_usage(service, model, 0, "error")
                        return
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk = line[6:]
                            if chunk == "[DONE]": break
                            try:
                                data = json.loads(chunk)
                                content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    total_tokens += 1
                                    yield content
                            except json.JSONDecodeError: continue
                    await self._log_usage(service, model, total_tokens, "success")
            except (httpx.ReadTimeout, httpx.ConnectError):
                await self._log_usage(service, model, total_tokens, "error")
                return
            except Exception as e:
                await self._log_usage(service, model, total_tokens, "error")
                return

    async def gemini_chat(self, prompt, model="gemini-2.0-flash", temperature=0.7, max_tokens=1024) -> Dict[str, Any]:
        url = f"{self.gemini_base}/{model}:generateContent?key={self.gemini_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                logger.info(f"Gemini: {tokens} tokens")
                try:
                    from models.core import UsageLog
                    await UsageLog(project="general", endpoint="/chat", provider="gemini", model=model, tokens_used=tokens, status="success").insert()
                except Exception: pass
                return {"success": True, "reply": data["candidates"][0]["content"]["parts"][0]["text"], "model": model, "tokens_used": tokens}
            except Exception as e:
                logger.error(f"Gemini: {str(e)[:200]}")
                return {"success": False, "error": "Gemini unavailable."}

    async def gemini_image(self, prompt, model="gemini-2.0-flash", num_images=1) -> Dict[str, Any]:
        try:
            result = await self.gemini_chat(prompt=f"Describe this image: {prompt}. Include composition, colors, lighting, style. Keep under 200 words.", model=model, temperature=0.9, max_tokens=400)
            return {"success": True, "images": [], "description": result.get("reply", ""), "model": f"{model} (text)", "note": "Image generation requires Imagen model — text description provided instead"}
        except: return {"success": False, "error": "Image description failed."}

    async def gemini_vision(self, prompt, image_base64=None, model="gemini-2.0-flash") -> Dict[str, Any]:
        url = f"{self.gemini_base}/{model}:generateContent?key={self.gemini_key}"
        parts = [{"text": prompt}]
        if image_base64: parts.append({"inlineData": {"mimeType": "image/jpeg", "data": image_base64}})
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(url, json={"contents": [{"parts": parts}]})
                response.raise_for_status()
                return {"success": True, "analysis": response.json()["candidates"][0]["content"]["parts"][0]["text"], "model": model}
            except: return {"success": False, "error": "Vision failed."}


ai_service = AIService()