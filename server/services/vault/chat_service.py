# ====================================================================================================
# server/services/vault/chat_service.py
# ====================================================================================================
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from models.general.conversation import Conversation, Message, MessageRole
from services.ai_service import ai_service

class VaultChatService:
    MAX_HISTORY = 15

    async def chat(self, user_id: str, message: str, conversation_id: Optional[str] = None, feature: str = "public") -> Dict[str, Any]:
        conversation = None
        if conversation_id:
            conversation = await Conversation.get(conversation_id)
        if not conversation:
            conversation = Conversation(user_id=user_id, title="Vault Chat")
            await conversation.insert()
            conversation_id = str(conversation.id)

        await Message(conversation_id=conversation_id, role=MessageRole.USER, content=message).insert()

        history = await Message.find(Message.conversation_id == conversation_id).sort(-Message.timestamp).limit(self.MAX_HISTORY).to_list()
        history.reverse()
        messages = [{"role": m.role.value, "content": m.content} for m in history]

        system_prompts = {
            "public": "You are HDM Vault AI. Answer questions about cybersecurity, password management, and data protection. Be educational and encourage signup for Pro features.",
            "private": "You are HDM Vault AI assistant for Pro users. Provide detailed cybersecurity advice, scan analysis, and security recommendations. Be thorough and professional.",
        }
        messages.insert(0, {"role": "system", "content": system_prompts.get(feature, system_prompts["public"])})

        result = await ai_service.groq_chat(messages, max_tokens=800)
        reply = result.get("reply", "Sorry, I couldn't process that.")

        await Message(conversation_id=conversation_id, role=MessageRole.ASSISTANT, content=reply, tokens_used=result.get("tokens_used", 0)).insert()

        conversation.message_count += 2
        conversation.updated_at = datetime.utcnow()
        await conversation.save()

        return {"reply": reply, "conversation_id": conversation_id, "tokens_used": result.get("tokens_used", 0)}

vault_chat_service = VaultChatService()