# ====================================================================================================
# server/services/widget/chat_service.py
# ====================================================================================================
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from models.widget.conversation import Conversation, Message, MessageRole
from services.ai_service import ai_service

class WidgetChatService:
    MAX_HISTORY = 15

    async def chat(
        self,
        source: str,
        message: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> Dict[str, Any]:
        conversation = None
        if conversation_id:
            conversation = await Conversation.get(conversation_id)
        if not conversation:
            conversation = Conversation(source=source, user_id=user_id)
            await conversation.insert()
            conversation_id = str(conversation.id)

        await Message(conversation_id=conversation_id, role=MessageRole.USER, content=message).insert()

        history = await Message.find(Message.conversation_id == conversation_id).sort(-Message.timestamp).limit(self.MAX_HISTORY).to_list()
        history.reverse()
        messages = [{"role": m.role.value, "content": m.content} for m in history]

        # Build system prompt based on source
        system_prompts = {
            "docusoft": "You are DocuSoft AI assistant. Help with document management, PDF editing, e-signatures, and file organization. Be professional and helpful.",
            "hdm_portfolio": "You are HDM Portfolio AI assistant. Answer questions about HDM's services, projects, and company. The user is a potential client. Be welcoming and informative.",
        }

        system = system_prompts.get(source, system_prompts["hdm_portfolio"])

        # Add custom context if provided
        if context:
            context_str = ", ".join(f"{k}: {v}" for k, v in context.items())
            system += f" Additional context: {context_str}"

        messages.insert(0, {"role": "system", "content": system})

        result = await ai_service.groq_chat(messages, max_tokens=800)
        reply = result.get("reply", "Sorry, I couldn't process that.")

        await Message(conversation_id=conversation_id, role=MessageRole.ASSISTANT, content=reply, tokens_used=result.get("tokens_used", 0)).insert()

        conversation.message_count += 2
        conversation.updated_at = datetime.utcnow()
        await conversation.save()

        return {"reply": reply, "conversation_id": conversation_id, "source": source, "tokens_used": result.get("tokens_used", 0)}

widget_chat_service = WidgetChatService()