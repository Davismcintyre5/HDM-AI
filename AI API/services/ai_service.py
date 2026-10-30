# ====================================================================================================
# HDM AI Engine — Core AI Service
# Groq + Gemini | Failover | Response cleaning
# External systems only see provider: "HDM AI" and model: "HDM Nova"
# ====================================================================================================

import httpx
import re
from typing import Dict, Any, List
from loguru import logger
from config import settings
from services.key_resolver import key_resolver

STYLE_INSTRUCTION = "Use bullet points (•) for lists. Never use markdown tables. Keep responses clean and readable."
PUBLIC_PROVIDER = "HDM AI"
PUBLIC_MODEL = "HDM Nova"


class AIService:

    def __init__(self):
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.gemini_base = "https://generativelanguage.googleapis.com/v1beta/models"

    @staticmethod
    def _clean_response(text: str) -> str:
        if not text:
            return text
        if '</think>' in text and '<think>' not in text:
            idx = text.rfind('</think>')
            text = text[idx + len('</think>'):].strip()
        if "thinking process:" in text.lower() and "here's a" in text.lower():
            for marker in ["Output Generation.", "[Done]", "✅\n\n", "\n\n\n"]:
                idx = text.rfind(marker)
                if idx > 0:
                    text = text[idx + len(marker):].strip()
                    break
            else:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith(('Here are', 'Based on', 'We have', 'The apps', 'Our portfolio', 'Here is', 'These are')):
                        text = '\n'.join(lines[i:]).strip()
                        break
        if '<think>' in text and '</think>' not in text:
            lines = text.split('\n')
            clean_lines, found = [], False
            starters = ['Here', 'The', 'I ', 'We', 'Based', 'In ', 'You can', 'This is', 'Let me', 'Welcome', 'Hello', 'Hi ', 'Sure', 'Absolutely', 'That', 'What', 'How', 'Why', 'When', 'Where', 'To ', 'For ', 'At ', 'On ', 'It ', 'As ', 'If ', 'A ', 'An ', 'Our ']
            thinking = ["Here's a thinking process", "Here is a thinking process", "thinking process", "Analyze User Input", "Identify Key", "Formulate Response", "Draft Response", "Self-Correction"]
            for line in lines:
                if not found:
                    if '<think>' in line:
                        continue
                    stripped = line.strip()
                    if any(p in stripped for p in thinking):
                        continue
                    if re.match(r'^\d+\.\s+\*\*', stripped):
                        found = True
                        clean_lines.append(line)
                        continue
                    if any(stripped.startswith(s) for s in starters) and len(stripped) > 20:
                        found = True
                if found:
                    clean_lines.append(line)
            text = '\n'.join(clean_lines).strip() if clean_lines else ''
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        text = re.sub(r'={THINK}.*?={THINK}', '', text, flags=re.DOTALL).strip()
        return text.strip()

    # ================================================================================================
    # GROQ — single call
    # ================================================================================================

    async def _groq_call(
        self, messages: List[Dict[str, str]], key: str, model: str,
        temperature: float, max_tokens: int, timeout: int = 30,
    ) -> Dict[str, Any]:
        styled, has_system = [], False
        for m in messages:
            if m["role"] == "system":
                styled.append({"role": "system", "content": f"{m['content']}\n\n{STYLE_INSTRUCTION}"})
                has_system = True
            else:
                styled.append(m)
        if not has_system:
            styled.insert(0, {"role": "system", "content": STYLE_INSTRUCTION})

        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": styled, "temperature": temperature, "max_tokens": max_tokens, "stream": False}

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.post(self.groq_url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                tokens = data.get("usage", {}).get("total_tokens", 0)
                reply = self._clean_response(data["choices"][0]["message"]["content"])
                return {"success": True, "reply": reply, "tokens_used": tokens, "provider": PUBLIC_PROVIDER, "model": PUBLIC_MODEL}
            except Exception as e:
                err = str(e)
                logger.error(f"Groq: {err[:200]}")
                return {"success": False, "error": err, "rate_limited": "429" in err}

    # ================================================================================================
    # GROQ — with failover chain
    # ================================================================================================

    async def groq_chat(
        self, messages: List[Dict[str, str]], bucket: str = "chat",
        temperature: float = 0.7, max_tokens: int = 4096, timeout: int = 30,
    ) -> Dict[str, Any]:
        chain = [(bucket, "groq")]
        if bucket == "completion":
            chain.append(("completion", "groq_backup"))

        keys = await key_resolver.resolve_chain(chain)
        if not keys:
            return {"success": False, "error": "No keys configured."}

        for i, entry in enumerate(keys):
            result = await self._groq_call(
                messages, entry["key"], entry.get("model", "openai/gpt-oss-20b"),
                temperature, max_tokens, timeout,
            )
            if result.get("success"):
                return result
            if not result.get("rate_limited"):
                break
            if i < len(keys) - 1:
                logger.warning(f"Key {i+1} rate limited — failing over")

        return {"success": False, "error": "AI unavailable."}

    # ================================================================================================
    # GEMINI
    # ================================================================================================

    async def gemini_chat(
        self, messages: List[Dict[str, str]], bucket: str = "chat",
        temperature: float = 0.7, max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        resolved = await key_resolver.resolve(bucket, "gemini")
        if not resolved.get("key"):
            return {"success": False, "error": "Gemini not configured."}

        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        prompt = f"{STYLE_INSTRUCTION}\n\n{prompt}"

        url = f"{self.gemini_base}/{resolved.get('model', 'gemini-2.5-flash')}:generateContent?key={resolved['key']}"
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                reply = self._clean_response(data["candidates"][0]["content"]["parts"][0]["text"])
                return {"success": True, "reply": reply, "tokens_used": tokens, "provider": PUBLIC_PROVIDER, "model": PUBLIC_MODEL}
            except Exception as e:
                logger.error(f"Gemini: {str(e)[:200]}")
                return {"success": False, "error": "AI unavailable."}

    # ================================================================================================
    # UNIVERSAL — chat or gemini
    # ================================================================================================

    async def call(
        self, messages: List[Dict[str, str]], bucket: str = "chat",
        provider: str = "groq", temperature: float = 0.7,
        max_tokens: int = 4096, timeout: int = 30,
    ) -> Dict[str, Any]:
        if provider == "gemini":
            return await self.gemini_chat(messages, bucket, temperature, max_tokens)
        return await self.groq_chat(messages, bucket, temperature, max_tokens, timeout)


ai_service = AIService()