from typing import Dict, Any, Optional
from services.ai_service import ai_service

class AdminService:
    async def chat(self, message: str, messages: Optional[list] = None) -> Dict[str, Any]:
        history = messages or []
        history.append({"role": "user", "content": message})
        history.insert(0, {"role": "system", "content": "You are SmartPOS Admin AI. Help system administrators with platform-wide settings, user management, and system health."})

        result = await ai_service.groq_chat(history, max_tokens=1000, module="smartpos")
        reply = result.get("reply", "Sorry, I couldn't process that.")

        return {"reply": reply}

admin_service = AdminService()