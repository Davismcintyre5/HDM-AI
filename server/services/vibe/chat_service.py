# ====================================================================================================
# server/services/vibe/chat_service.py
# ====================================================================================================
from typing import Dict, Any, Optional
from services.ai_service import ai_service
from loguru import logger

class VibeChatService:
    async def chat_message(self, user_id: str, message: str, conversation_id: str = None) -> Dict[str, Any]:
        system = "You are Vibe Social AI. Help with social media, content creation, engagement, and trends. Be creative and encouraging."
        messages = [{"role": "system", "content": system}, {"role": "user", "content": message}]
        result = await ai_service.groq_chat(messages, max_tokens=800)
        return {"reply": result.get("reply", ""), "conversation_id": conversation_id or "new", "tokens_used": result.get("tokens_used", 0)}

    async def assistant(self, user_id: str, task: str, context: dict = None) -> Dict[str, Any]:
        prompt = f"Help with this task: {task}"
        if context: prompt += f"\nContext: {context}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=800)
        return {"reply": result.get("reply", "")}

    async def creative(self, user_id: str, prompt: str, style: str = None) -> Dict[str, Any]:
        full_prompt = prompt
        if style: full_prompt = f"Create in {style} style: {prompt}"
        result = await ai_service.groq_chat([{"role": "user", "content": full_prompt}], max_tokens=1000)
        return {"result": result.get("reply", "")}

vibe_chat_service = VibeChatService()