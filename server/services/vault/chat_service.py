# ====================================================================================================
# 5. server/services/vault/chat_service.py
# ====================================================================================================
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from models.general.conversation import Conversation, Message, MessageRole
from services.ai_service import ai_service
import json

class VaultChatService:
    MAX_HISTORY = 15

    async def chat(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        feature: str = "public",
        data: Optional[dict] = None,
    ) -> Dict[str, Any]:
        # Get or create conversation
        conversation = None
        if conversation_id:
            conversation = await Conversation.get(conversation_id)
        if not conversation:
            conversation = Conversation(user_id=user_id, title="Vault Chat")
            await conversation.insert()
            conversation_id = str(conversation.id)

        await Message(conversation_id=conversation_id, role=MessageRole.USER, content=message).insert()

        history = await Message.find(
            Message.conversation_id == conversation_id
        ).sort(-Message.timestamp).limit(self.MAX_HISTORY).to_list()
        history.reverse()
        messages = [{"role": m.role.value, "content": m.content} for m in history]

        # Build system prompt based on feature and data
        system_prompt = self._build_system_prompt(feature, data)
        messages.insert(0, {"role": "system", "content": system_prompt})

        result = await ai_service.groq_chat(messages, max_tokens=800)
        reply = result.get("reply", "Sorry, I couldn't process that.")

        await Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=reply,
            tokens_used=result.get("tokens_used", 0),
        ).insert()

        conversation.message_count += 2
        conversation.updated_at = datetime.utcnow()
        await conversation.save()

        return {
            "reply": reply,
            "conversation_id": conversation_id,
            "tokens_used": result.get("tokens_used", 0),
        }

    def _build_system_prompt(self, feature: str, data: Optional[dict] = None) -> str:
        base = "You are HDM Vault AI, a cybersecurity assistant."

        if feature == "public":
            base += " Answer general questions about cybersecurity, password management, and data protection. Be educational and encourage signup for Pro features."
            # No real data needed for public chat
        else:  # private
            if data and "user" in data:
                user = data["user"]
                context = (
                    f"\n\nREAL USER SECURITY DATA:\n"
                    f"- Total Passwords: {user.get('total_passwords', '?')}\n"
                    f"- Weak Passwords: {user.get('weak_passwords', '?')}\n"
                    f"- Reused Passwords: {user.get('reused_passwords', '?')}\n"
                    f"- Breached Accounts: {user.get('breached_accounts', '?')}\n"
                    f"- 2FA Enabled: {user.get('two_factor_enabled', False)}\n"
                    f"- Security Score: {user.get('security_score', '?')}/100\n"
                    f"- Last Full Scan: {user.get('last_full_scan', 'Never')}\n"
                    f"- Devices: {json.dumps(user.get('devices', []))}"
                )
                base += f"\n{context}\n\nUse this real security data to give personalized advice. Do not make up numbers."
            else:
                base += "\n\nThe user has not provided security data. If they ask about their security status, tell them to connect their Vault account or provide real security metrics."

        return base


vault_chat_service = VaultChatService()