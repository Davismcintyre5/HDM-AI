"""
HDM AI Engine - Chat Service
Stateless — receives messages from MERN, returns AI reply
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from services.ai_service import ai_service


class ChatService:
    MAX_HISTORY = 20

    async def chat(
        self,
        user_id: str,
        message: str,
        messages: Optional[List[Dict[str, str]]] = None,
        provider: str = "groq",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        search_enabled: bool = False,
        deep_think: bool = False,
        system_prompt: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Main chat handler — stateless. MERN provides everything."""

        messages_list = []

        if system_prompt:
            final_prompt = system_prompt
        else:
            final_prompt = self._build_dynamic_prompt(
                has_data=data is not None,
                deep_think=deep_think,
            )

        if data:
            import json
            data_str = json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
            final_prompt += f"\n\n[EXTERNAL DATA]\n{data_str[:4000]}"

        if deep_think:
            final_prompt += "\n\nUse chain-of-thought reasoning. Think step by step before answering."

        messages_list.insert(0, {"role": "system", "content": final_prompt})

        if messages:
            messages_list.extend(messages[-self.MAX_HISTORY:])

        if not messages or messages[-1].get("content") != message:
            messages_list.append({"role": "user", "content": message})

        if provider == "gemini":
            result = await ai_service.gemini_chat_full(
                messages_list,
                model=model or "gemini-2.5-flash",
                temperature=temperature,
                max_tokens=max_tokens,
                module="general",
            )
        else:
            result = await ai_service.groq_chat(
                messages_list,
                model=model or "openai/gpt-oss-20b",
                temperature=temperature,
                max_tokens=max_tokens,
                module="general",
            )

        reply = result.get("reply", "Sorry, I couldn't process that.")
        model_used = result.get("model", provider)

        suggestions = await self._generate_suggestions(message, reply)

        return {
            "reply": reply,
            "model": model_used,
            "tokens_used": result.get("tokens_used", 0),
            "provider": provider,
            "suggestions": suggestions,
            "external_data_used": data is not None,
            "deep_think_used": deep_think,
        }

    def _build_dynamic_prompt(self, has_data: bool = False, deep_think: bool = False) -> str:
        parts = [
            "You are HDM AI, a versatile and intelligent assistant.",
            "You help with general questions, learning, coding, content analysis, business intelligence, and more.",
            "Be warm, natural, and conversational. Adapt your tone to the user's needs.",
            "When appropriate, be concise. When detail is needed, be thorough.",
        ]
        if has_data:
            parts.append("The user has connected external business systems. Analyze the provided data and give insights based on it.")
        return "\n\n".join(parts)

    async def _generate_suggestions(self, user_msg: str, ai_reply: str) -> List[str]:
        try:
            result = await ai_service.groq_chat(
                messages=[
                    {"role": "system", "content": "Generate 3 follow-up questions. Output ONLY the questions, one per line."},
                    {"role": "user", "content": f"User: {user_msg}\nAssistant: {ai_reply[:150]}\n\nFollow-up questions:"},
                ],
                temperature=0.5, max_tokens=200, module="general",
            )
            if result.get("success"):
                reply = result["reply"]
                lines = [s.strip().lstrip("1234567890. -•*#") for s in reply.split("\n") if s.strip() and len(s.strip()) > 10]
                return lines[:3]
        except:
            pass
        return []


chat_service = ChatService()