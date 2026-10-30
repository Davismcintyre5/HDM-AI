# ====================================================================================================
# HDM AI Engine — Chat Service (/v1/chat)
# Frontend chat | Key 1 or Gemini (admin toggle)
# ====================================================================================================

import json
from typing import Dict, Any, List, Optional
from services.ai_service import ai_service, PUBLIC_PROVIDER, PUBLIC_MODEL


class ChatService:
    MAX_HISTORY = 20

    async def chat(
        self, user_id: str, message: str,
        messages: Optional[List[Dict[str, str]]] = None,
        provider: str = "groq", model: Optional[str] = None,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        search_enabled: bool = False, deep_think: bool = False,
    ) -> Dict[str, Any]:
        messages_list = []
        prompt = system_prompt or self._build_prompt(data is not None, deep_think)

        if data:
            data_str = json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
            prompt += f"\n\n[EXTERNAL DATA]\n{data_str[:4000]}"

        if deep_think:
            prompt += "\n\nThink step by step before answering."

        messages_list.insert(0, {"role": "system", "content": prompt})

        if messages:
            messages_list.extend(messages[-self.MAX_HISTORY:])

        if not messages or messages[-1].get("content") != message:
            messages_list.append({"role": "user", "content": message})

        result = await ai_service.call(
            messages_list, bucket="chat", provider=provider,
            temperature=temperature, max_tokens=max_tokens,
        )

        reply = result.get("reply", "Sorry, I couldn't process that.")

        return {
            "reply": reply,
            "model": PUBLIC_MODEL,
            "tokens_used": result.get("tokens_used", 0),
            "provider": PUBLIC_PROVIDER,
            "suggestions": await self._suggestions(message, reply, provider),
            "external_data_used": data is not None,
            "deep_think_used": deep_think,
        }

    def _build_prompt(self, has_data: bool, deep_think: bool) -> str:
        parts = [
            "You are HDM AI, a versatile and intelligent assistant.",
            "You help with general questions, learning, coding, content analysis, and business intelligence.",
            "Be warm, natural, and conversational.",
        ]
        if has_data:
            parts.append("Analyze the provided business data and give insights.")
        return "\n\n".join(parts)

    async def _suggestions(self, user_msg: str, reply: str, provider: str) -> List[str]:
        try:
            msgs = [
                {"role": "system", "content": "Generate 3 follow-up questions. Output ONLY the questions, one per line."},
                {"role": "user", "content": f"User: {user_msg}\nAssistant: {reply[:150]}\n\nFollow-up questions:"},
            ]
            result = await ai_service.call(msgs, bucket="chat", provider=provider, temperature=0.5, max_tokens=200)
            if result.get("success"):
                return [s.strip().lstrip("1234567890. -•*#") for s in result["reply"].split("\n") if s.strip() and len(s.strip()) > 10][:3]
        except Exception:
            pass
        return []


chat_service = ChatService()