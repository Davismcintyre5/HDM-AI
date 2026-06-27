from typing import Dict, Any, List
from services.ai_service import ai_service

class SmartReplyService:
    def _build_context(self, data: dict = None) -> str:
        if not data: return ""
        parts = []
        if "recent_messages" in data:
            parts.append("Recent conversation:\n" + "\n".join([m.get('content','') for m in data['recent_messages'][:5]]))
        if "user_preferences" in data and "common_phrases" in data["user_preferences"]:
            parts.append(f"User's common phrases: {', '.join(data['user_preferences']['common_phrases'])}")
        return "\n".join(parts) if parts else ""

    async def reply(self, message: str, count: int = 3, tone: str = None, data: dict = None) -> Dict[str, Any]:
        context = self._build_context(data)
        prompt = f"{context}\nGenerate {count} short replies to: '{message}'."
        if tone: prompt += f" Use {tone} tone."
        prompt += " One per line."
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=150, module="spark")
        return {"replies": [r.strip() for r in result.get("reply", "").split("\n") if r.strip()][:count]}

    async def quick_reply(self, message: str, count: int = 4, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Generate {count} very short replies (1-3 words) to: '{message}'. One per line."}], max_tokens=80, module="spark")
        return {"quick_replies": [r.strip() for r in result.get("reply", "").split("\n") if r.strip()][:count]}

    async def reply_with_context(self, message: str, previous_messages: List[str], data: dict = None) -> Dict[str, Any]:
        context = "\n".join(previous_messages[-5:])
        result = await ai_service.groq_chat([{"role": "user", "content": f"Previous:\n{context}\n\nSuggest a reply to: {message}"}], max_tokens=200, module="spark")
        return {"reply": result.get("reply", "")}

    async def reply_with_tone(self, message: str, target_tone: str = "friendly", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Reply to '{message}' in a {target_tone} tone."}], max_tokens=200, module="spark")
        return {"reply": result.get("reply", "")}

    async def reply_in_language(self, message: str, language: str = "en", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Reply to '{message}' in {language}."}], max_tokens=200, module="spark")
        return {"reply": result.get("reply", "")}

smart_reply_service = SmartReplyService()