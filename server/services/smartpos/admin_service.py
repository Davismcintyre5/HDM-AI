# ====================================================================================================
# 16. server/services/smartpos/admin_service.py
# ====================================================================================================
from typing import Dict, Any, Optional
from datetime import datetime
from models.smartpos.conversation import Conversation, Message, MessageRole
from services.ai_service import ai_service
from loguru import logger

class AdminService:
    async def chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        conversation = None
        if conversation_id: conversation = await Conversation.get(conversation_id)
        if not conversation:
            conversation = Conversation(client_id="admin", title="Admin Chat")
            await conversation.insert()
            conversation_id = str(conversation.id)

        await Message(conversation_id=conversation_id, role=MessageRole.USER, content=message).insert()

        history = await Message.find(Message.conversation_id == conversation_id).sort(-Message.timestamp).limit(10).to_list()
        history.reverse()
        messages = [{"role": m.role.value, "content": m.content} for m in history]
        messages.insert(0, {"role": "system", "content": "You are SmartPOS Admin AI. Help system administrators with platform-wide settings, user management, and system health."})

        result = await ai_service.groq_chat(messages, max_tokens=1000, service="smartpos")
        reply = result.get("reply", "Sorry, I couldn't process that.")

        await Message(conversation_id=conversation_id, role=MessageRole.ASSISTANT, content=reply, tokens_used=result.get("tokens_used", 0)).insert()

        conversation.message_count += 2; conversation.updated_at = datetime.utcnow()
        await conversation.save()
        return {"reply": reply, "conversation_id": conversation_id}

admin_service = AdminService()