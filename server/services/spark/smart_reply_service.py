# ====================================================================================================
# server/services/spark/smart_reply_service.py
# ====================================================================================================
from typing import Dict, Any, List
from services.ai_service import ai_service

class SmartReplyService:
    async def reply(self, message: str, count: int = 3, tone: str = None) -> Dict[str, Any]:
        prompt = f"Generate {count} short, quick replies to: '{message}'."
        if tone: prompt += f" Use a {tone} tone."
        prompt += " Return one per line."
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=150)
        replies = [r.strip() for r in result.get("reply", "").split("\n") if r.strip()]
        return {"replies": replies[:count]}

    async def quick_reply(self, message: str, count: int = 4) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Generate {count} very short quick replies (1-3 words) to: '{message}'. One per line."}], max_tokens=80)
        replies = [r.strip() for r in result.get("reply", "").split("\n") if r.strip()]
        return {"quick_replies": replies[:count]}

    async def reply_with_context(self, message: str, previous_messages: List[str]) -> Dict[str, Any]:
        context = "\n".join(previous_messages[-5:])
        result = await ai_service.groq_chat([{"role": "user", "content": f"Previous:\n{context}\n\nSuggest a reply to: {message}"}], max_tokens=200)
        return {"reply": result.get("reply", "")}

    async def reply_with_tone(self, message: str, target_tone: str = "friendly") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Reply to '{message}' in a {target_tone} tone."}], max_tokens=200)
        return {"reply": result.get("reply", "")}

    async def reply_in_language(self, message: str, language: str = "en") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Reply to '{message}' in {language}."}], max_tokens=200)
        return {"reply": result.get("reply", "")}

smart_reply_service = SmartReplyService()