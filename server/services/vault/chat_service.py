# ====================================================================================================
# 36. server/services/vault/chat_service.py
# ====================================================================================================
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from models.general.conversation import Conversation, Message, MessageRole
from services.ai_service import ai_service
import json

class VaultChatService:
    MAX_HISTORY = 15

    async def chat(self, user_id: str, message: str, conversation_id: Optional[str] = None, feature: str = "public", data: Optional[dict] = None) -> Dict[str, Any]:
        conversation = None
        if conversation_id: conversation = await Conversation.get(conversation_id)
        if not conversation:
            conversation = Conversation(user_id=user_id, title="Vault Chat")
            await conversation.insert(); conversation_id = str(conversation.id)

        await Message(conversation_id=conversation_id, role=MessageRole.USER, content=message).insert()

        history = await Message.find(Message.conversation_id == conversation_id).sort(-Message.timestamp).limit(self.MAX_HISTORY).to_list()
        history.reverse()
        messages = [{"role": m.role.value, "content": m.content} for m in history]
        system_prompt = self._build_system_prompt(feature, data)
        messages.insert(0, {"role": "system", "content": system_prompt})

        result = await ai_service.groq_chat(messages, max_tokens=800, service="vault")
        reply = result.get("reply", "Sorry, I couldn't process that.")

        await Message(conversation_id=conversation_id, role=MessageRole.ASSISTANT, content=reply, tokens_used=result.get("tokens_used", 0)).insert()
        conversation.message_count += 2; conversation.updated_at = datetime.utcnow(); await conversation.save()
        return {"reply": reply, "conversation_id": conversation_id, "tokens_used": result.get("tokens_used", 0)}

    def _build_system_prompt(self, feature: str, data: Optional[dict] = None) -> str:
        base = "You are HDM Vault AI, a cybersecurity assistant."
        if feature == "public":
            base += " Answer general questions about cybersecurity. Be educational."
        else:
            if data and "user" in data:
                user = data["user"]
                base += f"\n\nREAL USER SECURITY DATA:\n- Total Passwords: {user.get('total_passwords','?')}\n- Weak: {user.get('weak_passwords','?')}\n- Breached: {user.get('breached_accounts','?')}\n- 2FA: {user.get('two_factor_enabled',False)}\n- Score: {user.get('security_score','?')}/100\nUse this real data."
            else:
                base += "\n\nNo security data provided. Tell user to connect their Vault account."
        return base

vault_chat_service = VaultChatService()