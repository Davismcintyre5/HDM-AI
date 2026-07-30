# ====================================================================================================
# HDM AI Engine - services/ai_service.py
# Multi-provider AI: Groq + Gemini | Key resolver integration | Streaming
# ====================================================================================================

import httpx
import json
import asyncio
import re
from typing import Optional, Dict, Any, AsyncGenerator, List
from loguru import logger
from config import settings
from services.key_resolver import key_resolver

STYLE_INSTRUCTION = "Use bullet points (•) for lists. Never use markdown tables. Keep responses clean and readable."


class AIService:

    def __init__(self):
        self.groq_chat_url = "https://api.groq.com/openai/v1/chat/completions"
        self.gemini_base = "https://generativelanguage.googleapis.com/v1beta/models"

    @staticmethod
    def _clean_response(text: str) -> str:
        """Remove thinking tags and raw thinking blocks from reasoning models."""
        if not text:
            return text
        if '</think>' in text and '<think>' not in text:
            idx = text.rfind('</think>')
            text = text[idx + len('</think>'):].strip()
        if "thinking process:" in text.lower() and "here's a" in text.lower():
            markers = ["Output Generation.", "[Done]", "✅\n\n", "\n\n\n"]
            for marker in markers:
                idx = text.rfind(marker)
                if idx > 0:
                    text = text[idx + len(marker):].strip()
                    break
            else:
                lines = text.split('\n')
                clean_start = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(('Here are', 'Based on', 'We have', 'The apps', 'Our portfolio', 'Here is', 'These are')):
                        clean_start = i
                        break
                if clean_start > 0:
                    text = '\n'.join(lines[clean_start:]).strip()
        if '<think>' in text and '</think>' not in text:
            lines = text.split('\n')
            clean_lines = []
            found_response = False
            response_starters = [
                'Here', 'The', 'I ', 'We', 'Based', 'In ', 'RVNP', 'HDM',
                'Smart', 'NexGuard', 'You can', 'This is', 'Let me',
                'Welcome', 'Hello', 'Hi ', 'Sure', 'Absolutely',
                'That', 'What', 'How', 'Why', 'When', 'Where',
                'To ', 'For ', 'At ', 'On ', 'By ', 'With ',
                'It ', 'As ', 'If ', 'A ', 'An ', 'Our ',
            ]
            thinking_phrases = [
                "Here's a thinking process", "Here is a thinking process",
                "thinking process", "Analyze User Input", "Identify Key",
                "Formulate Response", "Draft Response", "Self-Correction",
            ]
            for line in lines:
                if not found_response:
                    if '<think>' in line: continue
                    stripped = line.strip()
                    if any(p in stripped for p in thinking_phrases): continue
                    if re.match(r'^\d+\.\s+\*\*', stripped):
                        found_response = True
                        clean_lines.append(line)
                        continue
                    if any(stripped.startswith(s) for s in response_starters) and len(stripped) > 20:
                        found_response = True
                if found_response:
                    clean_lines.append(line)
            if clean_lines:
                text = '\n'.join(clean_lines).strip()
            else:
                text = ''
        if re.search(r'^\d+\.\s+\*\*.*\*\*', text, re.MULTILINE):
            lines = text.split('\n')
            clean_lines = []
            found = False
            for line in lines:
                stripped = line.strip()
                if not found:
                    if re.match(r'^\d+\.\s+\*\*', stripped): continue
                    if stripped and not stripped.startswith(('•', '-', '*')):
                        found = True
                if found:
                    clean_lines.append(line)
            if clean_lines:
                text = '\n'.join(clean_lines).strip()
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        text = re.sub(r'={THINK}.*?={THINK}', '', text, flags=re.DOTALL).strip()
        return text.strip()

    # ================================================================================================
    # GROQ CHAT
    # ================================================================================================

    async def groq_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-oss-20b",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: int = 30,
        module: str = "general",
    ) -> Dict[str, Any]:
        resolved = await key_resolver.resolve(module, "groq")
        if not resolved.get("key"):
            return {"success": False, "error": "No Groq key configured for this module."}

        # Inject style instruction into system prompt
        styled_messages = []
        for m in messages:
            if m["role"] == "system":
                styled_messages.append({"role": "system", "content": f"{m['content']}\n\n{STYLE_INSTRUCTION}"})
            else:
                styled_messages.append(m)
        if not any(m["role"] == "system" for m in messages):
            styled_messages.insert(0, {"role": "system", "content": STYLE_INSTRUCTION})

        headers = {
            "Authorization": f"Bearer {resolved['key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": resolved.get("model", model),
            "messages": styled_messages,
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
                reply = self._clean_response(data["choices"][0]["message"]["content"])
                logger.info(f"Groq[{module}]: {tokens} tokens")
                return {
                    "success": True,
                    "reply": reply,
                    "model": resolved.get("model", model),
                    "tokens_used": tokens,
                }
            except Exception as e:
                error_str = str(e)
                logger.error(f"Groq[{module}]: {error_str[:200]}")
                if "429" in error_str:
                    logger.warning(f"Groq[{module}] rate limited — retrying in 10s...")
                    await asyncio.sleep(10)
                    try:
                        response = await client.post(self.groq_chat_url, headers=headers, json=payload)
                        response.raise_for_status()
                        data = response.json()
                        tokens = data.get("usage", {}).get("total_tokens", 0)
                        reply = self._clean_response(data["choices"][0]["message"]["content"])
                        logger.info(f"Groq[{module}] retry OK: {tokens} tokens")
                        return {
                            "success": True,
                            "reply": reply,
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
        model: str = "openai/gpt-oss-20b",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        module: str = "general",
    ) -> AsyncGenerator[str, None]:
        resolved = await key_resolver.resolve(module, "groq")
        if not resolved.get("key"):
            return

        styled_messages = []
        for m in messages:
            if m["role"] == "system":
                styled_messages.append({"role": "system", "content": f"{m['content']}\n\n{STYLE_INSTRUCTION}"})
            else:
                styled_messages.append(m)
        if not any(m["role"] == "system" for m in messages):
            styled_messages.insert(0, {"role": "system", "content": STYLE_INSTRUCTION})

        headers = {
            "Authorization": f"Bearer {resolved['key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": resolved.get("model", model),
            "messages": styled_messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                async with client.stream("POST", self.groq_chat_url, headers=headers, json=payload) as response:
                    if response.status_code != 200: return
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk = line[6:]
                            if chunk == "[DONE]": break
                            try:
                                data = json.loads(chunk)
                                content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content: yield content
                            except json.JSONDecodeError: continue
            except (httpx.ReadTimeout, httpx.ConnectError): return
            except Exception as e:
                logger.error(f"Groq stream[{module}]: {str(e)[:200]}")

    # ================================================================================================
    # GEMINI CHAT
    # ================================================================================================

    async def gemini_chat(
        self, prompt: str, model: str = "gemini-2.5-flash", temperature: float = 0.7,
        max_tokens: int = 4096, module: str = "general",
    ) -> Dict[str, Any]:
        resolved = await key_resolver.resolve(module, "gemini")
        if not resolved.get("key"):
            return {"success": False, "error": "No Gemini key configured."}

        prompt = f"{STYLE_INSTRUCTION}\n\n{prompt}"

        url = f"{self.gemini_base}/{resolved.get('model', model)}:generateContent?key={resolved['key']}"
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                reply = self._clean_response(data["candidates"][0]["content"]["parts"][0]["text"])
                logger.info(f"Gemini[{module}]: {tokens} tokens")
                return {"success": True, "reply": reply, "model": resolved.get("model", model), "tokens_used": tokens}
            except Exception as e:
                logger.error(f"Gemini[{module}]: {str(e)[:200]}")
                return {"success": False, "error": "Gemini unavailable."}

    # ================================================================================================
    # GEMINI CHAT FULL
    # ================================================================================================

    async def gemini_chat_full(
        self, messages: List[Dict[str, str]], model: str = "gemini-2.5-flash",
        temperature: float = 0.7, max_tokens: int = 4096, timeout: int = 30, module: str = "general",
    ) -> Dict[str, Any]:
        resolved = await key_resolver.resolve(module, "gemini")
        if not resolved.get("key"):
            return {"success": False, "error": "No Gemini key configured."}

        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        prompt = f"{STYLE_INSTRUCTION}\n\n{prompt}"

        url = f"{self.gemini_base}/{resolved.get('model', model)}:generateContent?key={resolved['key']}"
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                reply = self._clean_response(data["candidates"][0]["content"]["parts"][0]["text"])
                logger.info(f"Gemini[{module}]: {tokens} tokens")
                return {"success": True, "reply": reply, "model": resolved.get("model", model), "tokens_used": tokens}
            except Exception as e:
                logger.error(f"Gemini[{module}]: {str(e)[:200]}")
                return {"success": False, "error": "Gemini unavailable."}

    # ================================================================================================
    # GEMINI VISION
    # ================================================================================================

    async def gemini_vision(
        self, prompt: str, image_base64: str = None, model: str = "gemini-2.5-flash", module: str = "general"
    ) -> Dict[str, Any]:
        resolved = await key_resolver.resolve(module, "gemini")
        if not resolved.get("key"):
            return {"success": False, "error": "No Gemini key configured."}

        url = f"{self.gemini_base}/{resolved.get('model', model)}:generateContent?key={resolved['key']}"
        parts = [{"text": prompt}]
        if image_base64: parts.append({"inlineData": {"mimeType": "image/jpeg", "data": image_base64}})

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(url, json={"contents": [{"parts": parts}]})
                response.raise_for_status()
                data = response.json()
                return {"success": True, "analysis": data["candidates"][0]["content"]["parts"][0]["text"], "model": resolved.get("model", model)}
            except Exception as e:
                logger.error(f"Gemini Vision[{module}]: {str(e)[:200]}")
                return {"success": False, "error": "Vision analysis failed."}

    # ================================================================================================
    # GEMINI IMAGE
    # ================================================================================================

    async def gemini_image(self, prompt: str, model: str = "gemini-2.5-flash", num_images: int = 1, module: str = "general") -> Dict[str, Any]:
        try:
            result = await self.gemini_chat(
                prompt=f"Describe this image: {prompt}. Include composition, colors, lighting, style. Keep under 200 words.",
                model=model, temperature=0.9, max_tokens=400, module=module,
            )
            return {"success": True, "images": [], "description": result.get("reply", ""), "model": f"{model} (text)", "note": "Image generation requires Imagen model — text description provided instead"}
        except Exception:
            return {"success": False, "error": "Image description failed."}


ai_service = AIService()