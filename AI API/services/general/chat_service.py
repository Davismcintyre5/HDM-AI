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
        max_tokens: int = 1024,
        search_enabled: bool = False,
        deep_think: bool = False,
        system_prompt: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Main chat handler — stateless. MERN provides everything."""

        # Build messages list
        messages_list = []

        # System prompt
        if system_prompt:
            final_prompt = system_prompt
        else:
            final_prompt = self._build_dynamic_prompt(
                has_data=data is not None,
                deep_think=deep_think,
            )

        # Add data context if provided
        if data:
            import json
            data_str = json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
            final_prompt += f"\n\n[EXTERNAL DATA]\n{data_str[:4000]}"

        if deep_think:
            final_prompt += "\n\nUse chain-of-thought reasoning. Think step by step before answering."

        messages_list.insert(0, {"role": "system", "content": final_prompt})

        # Add conversation history from MERN
        if messages:
            messages_list.extend(messages[-self.MAX_HISTORY:])

        # Add current user message if not already in history
        if not messages or messages[-1].get("content") != message:
            messages_list.append({"role": "user", "content": message})

        # Call AI
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
                model=model or "llama-3.3-70b-versatile",
                temperature=temperature,
                max_tokens=max_tokens,
                module="general",
            )

        reply = result.get("reply", "Sorry, I couldn't process that.")
        model_used = result.get("model", provider)

        # Generate suggestions
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

    # ================================================================================================
    # DYNAMIC SYSTEM PROMPT
    # ================================================================================================

    def _build_dynamic_prompt(
        self,
        has_data: bool = False,
        deep_think: bool = False,
    ) -> str:
        """Build a context-aware system prompt."""

        parts = [
            "You are HDM AI, a versatile and intelligent assistant.",
            "You help with general questions, learning, coding, content analysis, business intelligence, and more.",
            "Be warm, natural, and conversational. Adapt your tone to the user's needs.",
            "When appropriate, be concise. When detail is needed, be thorough.",
        ]

        if has_data:
            parts.append(
                "The user has connected external business systems. "
                "Analyze the provided data and give insights based on it."
            )

        return "\n\n".join(parts)

    # ================================================================================================
    # SUGGESTIONS
    # ================================================================================================

    async def _generate_suggestions(self, user_msg: str, ai_reply: str) -> List[str]:
        """Generate follow-up questions."""
        try:
            result = await ai_service.groq_chat(
                messages=[
                    {"role": "system", "content": "Generate 3 follow-up questions. One per line, no numbers."},
                    {"role": "user", "content": f"User: {user_msg}\nAssistant: {ai_reply[:300]}"},
                ],
                temperature=0.8,
                max_tokens=100,
                module="general",
            )
            if result.get("success"):
                return [s.strip() for s in result["reply"].split("\n") if s.strip()][:3]
        except Exception:
            pass
        return []


chat_service = ChatService()