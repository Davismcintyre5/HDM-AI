# ====================================================================================================
# HDM AI Engine - services/ai_service.py
# Multi-provider AI: Groq + Gemini | Key resolver integration | Streaming
# ====================================================================================================

import httpx
import json
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator, List
from loguru import logger
from config import settings
from services.key_resolver import key_resolver


class AIService:

    def __init__(self):
        self.groq_chat_url = "https://api.groq.com/openai/v1/chat/completions"
        self.gemini_base = "https://generativelanguage.googleapis.com/v1beta/models"

    # ================================================================================================
    # GROQ CHAT
    # ================================================================================================

    async def groq_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 30,
        module: str = "general",
    ) -> Dict[str, Any]:
        """Groq chat — resolves key per module."""
        resolved = await key_resolver.resolve(module, "groq")
        if not resolved.get("key"):
            return {"success": False, "error": "No Groq key configured for this module."}

        headers = {
            "Authorization": f"Bearer {resolved['key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": resolved.get("model", model),
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
                tokens = data.get("usage", {}).get("total_tokens", 0)
                logger.info(f"Groq[{module}]: {tokens} tokens")
                return {
                    "success": True,
                    "reply": data["choices"][0]["message"]["content"],
                    "model": resolved.get("model", model),
                    "tokens_used": tokens,
                }
            except Exception as e:
                error_str = str(e)
                logger.error(f"Groq[{module}]: {error_str[:200]}")

                # Retry once on rate limit
                if "429" in error_str:
                    logger.warning(f"Groq[{module}] rate limited — retrying in 10s...")
                    await asyncio.sleep(10)
                    try:
                        response = await client.post(self.groq_chat_url, headers=headers, json=payload)
                        response.raise_for_status()
                        data = response.json()
                        tokens = data.get("usage", {}).get("total_tokens", 0)
                        logger.info(f"Groq[{module}] retry OK: {tokens} tokens")
                        return {
                            "success": True,
                            "reply": data["choices"][0]["message"]["content"],
                            "model": resolved.get("model", model),
                            "tokens_used": tokens,
                        }
                    except Exception as retry_err:
                        logger.error(f"Groq[{module}] retry failed: {str(retry_err)[:200]}")
                        return {"success": False, "error": "AI service temporarily unavailable."}

                return {"success": False, "error": "AI service unavailable."}

    # ================================================================================================
    # GROQ STREAMING
    # ================================================================================================

    async def groq_chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        module: str = "general",
    ) -> AsyncGenerator[str, None]:
        """Groq streaming chat — yields tokens as they arrive."""
        resolved = await key_resolver.resolve(module, "groq")
        if not resolved.get("key"):
            return

        headers = {
            "Authorization": f"Bearer {resolved['key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": resolved.get("model", model),
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                async with client.stream("POST", self.groq_chat_url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
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
                return
            except Exception as e:
                logger.error(f"Groq stream[{module}]: {str(e)[:200]}")
                return

    # ================================================================================================
    # GEMINI CHAT (simple — single prompt string)
    # ================================================================================================

    async def gemini_chat(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        module: str = "general",
    ) -> Dict[str, Any]:
        """Gemini chat — simple prompt in, reply out."""
        resolved = await key_resolver.resolve(module, "gemini")
        if not resolved.get("key"):
            return {"success": False, "error": "No Gemini key configured."}

        url = f"{self.gemini_base}/{resolved.get('model', model)}:generateContent?key={resolved['key']}"
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
                tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"Gemini[{module}]: {tokens} tokens")
                return {
                    "success": True,
                    "reply": reply,
                    "model": resolved.get("model", model),
                    "tokens_used": tokens,
                }
            except Exception as e:
                logger.error(f"Gemini[{module}]: {str(e)[:200]}")
                return {"success": False, "error": "Gemini unavailable."}

    # ================================================================================================
    # GEMINI CHAT FULL (messages list — drop-in replacement for groq_chat)
    # ================================================================================================

    async def gemini_chat_full(
        self,
        messages: List[Dict[str, str]],
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 30,
        module: str = "general",
    ) -> Dict[str, Any]:
        """Gemini chat with full messages list — same signature as groq_chat."""
        resolved = await key_resolver.resolve(module, "gemini")
        if not resolved.get("key"):
            return {"success": False, "error": "No Gemini key configured."}

        # Convert messages list to a single Gemini prompt
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

        url = f"{self.gemini_base}/{resolved.get('model', model)}:generateContent?key={resolved['key']}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"Gemini[{module}]: {tokens} tokens")
                return {
                    "success": True,
                    "reply": reply,
                    "model": resolved.get("model", model),
                    "tokens_used": tokens,
                }
            except Exception as e:
                logger.error(f"Gemini[{module}]: {str(e)[:200]}")
                return {"success": False, "error": "Gemini unavailable."}

    # ================================================================================================
    # GEMINI VISION
    # ================================================================================================

    async def gemini_vision(
        self,
        prompt: str,
        image_base64: str = None,
        model: str = "gemini-2.5-flash",
        module: str = "general",
    ) -> Dict[str, Any]:
        """Gemini vision — analyze image with prompt."""
        resolved = await key_resolver.resolve(module, "gemini")
        if not resolved.get("key"):
            return {"success": False, "error": "No Gemini key configured."}

        url = f"{self.gemini_base}/{resolved.get('model', model)}:generateContent?key={resolved['key']}"
        parts = [{"text": prompt}]
        if image_base64:
            parts.append({"inlineData": {"mimeType": "image/jpeg", "data": image_base64}})

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(url, json={"contents": [{"parts": parts}]})
                response.raise_for_status()
                data = response.json()
                return {
                    "success": True,
                    "analysis": data["candidates"][0]["content"]["parts"][0]["text"],
                    "model": resolved.get("model", model),
                }
            except Exception as e:
                logger.error(f"Gemini Vision[{module}]: {str(e)[:200]}")
                return {"success": False, "error": "Vision analysis failed."}

    # ================================================================================================
    # GEMINI IMAGE (text description — placeholder for Imagen)
    # ================================================================================================

    async def gemini_image(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        num_images: int = 1,
        module: str = "general",
    ) -> Dict[str, Any]:
        """Image generation placeholder — returns text description."""
        try:
            result = await self.gemini_chat(
                prompt=f"Describe this image: {prompt}. Include composition, colors, lighting, style. Keep under 200 words.",
                model=model,
                temperature=0.9,
                max_tokens=400,
                module=module,
            )
            return {
                "success": True,
                "images": [],
                "description": result.get("reply", ""),
                "model": f"{model} (text)",
                "note": "Image generation requires Imagen model — text description provided instead",
            }
        except Exception:
            return {"success": False, "error": "Image description failed."}


# Singleton
ai_service = AIService()