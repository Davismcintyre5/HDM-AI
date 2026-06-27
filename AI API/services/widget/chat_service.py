from typing import Dict, Any, Optional
from services.ai_service import ai_service

class WidgetChatService:
    MAX_HISTORY = 15

    async def chat(self, source: str, message: str, messages: Optional[list] = None, user_id: Optional[str] = None, context: Optional[dict] = None) -> Dict[str, Any]:
        history = messages or []
        history.append({"role": "user", "content": message})

        system_prompts = {
            "docusoft": "You are DocuSoft AI. Help with documents, pricing, and purchases.",
            "hdm_portfolio": "You are HDM Portfolio AI. Answer questions about our company, services, apps, and projects."
        }
        system = system_prompts.get(source, system_prompts["hdm_portfolio"])
        if context:
            context_str = ", ".join(f"{k}: {v}" for k, v in context.items())
            system += f" Additional context: {context_str}"

        history.insert(0, {"role": "system", "content": system})

        result = await ai_service.groq_chat(history, max_tokens=800, module="widget")
        reply = result.get("reply", "Sorry, I couldn't process that.")

        return {"reply": reply, "source": source, "tokens_used": result.get("tokens_used", 0)}

widget_chat_service = WidgetChatService()