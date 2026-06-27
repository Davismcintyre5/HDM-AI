from typing import Dict, Any, Optional
from services.ai_service import ai_service
import json

class VibeChatService:
    def _build_context(self, data: Optional[dict] = None) -> str:
        if not data: return ""
        parts = ["\n\nREAL USER DATA:"]
        if "user_profile" in data: parts.append(f"User: {json.dumps(data['user_profile'])}")
        if "recent_activity" in data: parts.append(f"Recent: {json.dumps(data['recent_activity'])}")
        parts.append("Use this real data. Do not make up information.")
        return "\n".join(parts)

    async def chat_message(self, user_id: str, message: str, conversation_id: str = None, data: dict = None) -> Dict[str, Any]:
        context = self._build_context(data)
        result = await ai_service.groq_chat([{"role": "system", "content": "You are Vibe Social AI. Help with social media and content." + context}, {"role": "user", "content": message}], max_tokens=800, module="vibe")
        return {"reply": result.get("reply", ""), "conversation_id": conversation_id or "new", "tokens_used": result.get("tokens_used", 0)}

    async def assistant(self, user_id: str, task: str, context: dict = None, data: dict = None) -> Dict[str, Any]:
        prompt = f"Help with: {task}"
        if context: prompt += f"\nContext: {context}"
        if data: prompt += f"\nData: {json.dumps(data)[:2000]}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=800, module="vibe")
        return {"reply": result.get("reply", "")}

    async def creative(self, user_id: str, prompt: str, style: str = None, data: dict = None) -> Dict[str, Any]:
        full_prompt = prompt
        if style: full_prompt = f"Create in {style} style: {prompt}"
        if data: full_prompt += f"\nContext: {json.dumps(data)[:1500]}"
        result = await ai_service.groq_chat([{"role": "user", "content": full_prompt}], max_tokens=1000, module="vibe")
        return {"result": result.get("reply", "")}

vibe_chat_service = VibeChatService()