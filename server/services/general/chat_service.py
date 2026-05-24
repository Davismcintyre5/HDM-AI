# ====================================================================================================
# server/services/general/chat_service.py — COMPLETE
# ====================================================================================================
"""
HDM AI - Chat Service with file upload, search toggle, deep think, external data, multi-provider
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import json

from models.general.conversation import Conversation, Message, MessageRole
from models.general.file_upload import FileUpload
from models.core import ThirdPartyKey
from services.ai_service import ai_service
from services.general.external_service import external_service
from services.general.file_service import file_service


class ChatService:
    MAX_HISTORY = 20

    async def chat(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        interface: str = "client",
        feature: str = "chat",
        search_enabled: bool = False,
        deep_think: bool = False,
        files: List = None,
        provider: str = "groq",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Main chat handler with all features."""

        # Get or create conversation
        conversation = None
        is_new_conversation = False
        if conversation_id:
            conversation = await Conversation.get(conversation_id)
        if not conversation:
            is_new_conversation = True
            conversation = Conversation(
                user_id=user_id,
                title=message[:50] + ("..." if len(message) > 50 else ""),
                interface=interface,
            )
            await conversation.insert()
            conversation_id = str(conversation.id)

        # Save user message
        await Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message,
        ).insert()

        # === FILE PROCESSING ===
        file_texts = []
        files_analyzed = 0
        if files:
            results = await file_service.extract_multiple(files)
            for r in results:
                if r["content"] and not r["content"].startswith("[Binary"):
                    file_texts.append(f"[File: {r['filename']}]\n{r['content']}")
                    files_analyzed += 1
                await FileUpload(
                    user_id=user_id,
                    filename=r["filename"],
                    original_name=r["filename"],
                    mime_type="unknown",
                    size_bytes=0,
                    path="",
                    extracted_text=r["content"][:1000],
                    conversation_id=conversation_id,
                ).insert()

        # === EXTERNAL DATA CHECK ===
        user_keys = await ThirdPartyKey.find(
            ThirdPartyKey.user_id == user_id,
            ThirdPartyKey.is_active == True,
        ).to_list()

        external_data = None
        if user_keys:
            detection = await self._detect_external_intent(message, user_keys)
            if detection.get("needs_external"):
                external_data = await self._fetch_and_format(user_id, detection, message)

        # === BUILD MESSAGES ===
        history = await Message.find(
            Message.conversation_id == conversation_id
        ).sort(-Message.timestamp).limit(self.MAX_HISTORY).to_list()
        history.reverse()
        messages_list = [{"role": m.role.value, "content": m.content} for m in history]

        # Build dynamic system prompt
        context_parts = []

        if file_texts:
            context_parts.append(
                "The user has uploaded files. Analyze them and answer based on their content:\n\n" +
                "\n---\n".join(file_texts)
            )

        if external_data:
            context_parts.append(external_data)

        if deep_think:
            context_parts.append(
                "Use chain-of-thought reasoning. Think step by step before answering. "
                "Break down complex problems, show your reasoning, then give a clear conclusion."
            )

        system_prompt = self._build_dynamic_prompt(
            interface=interface,
            is_new=is_new_conversation,
            has_keys=bool(user_keys),
            context="\n\n".join(context_parts) if context_parts else None,
        )
        messages_list.insert(0, {"role": "system", "content": system_prompt})

        # === CALL AI — Multi-provider support ===
        if provider == "gemini":
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages_list])
            result = await ai_service.gemini_chat(prompt, temperature=temperature, max_tokens=max_tokens)
            reply = result.get("reply", "Sorry, I couldn't process that.")
            model_used = result.get("model", "gemini")
        else:
            result = await ai_service.groq_chat(messages_list, temperature=temperature, max_tokens=max_tokens)
            reply = result.get("reply", "Sorry, I couldn't process that.")
            model_used = result.get("model", "groq")

        # Save assistant message
        await Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=reply,
            tokens_used=result.get("tokens_used", 0),
            model=model_used,
        ).insert()

        # Update conversation
        conversation.message_count += 2
        conversation.total_tokens += result.get("tokens_used", 0)
        conversation.updated_at = datetime.utcnow()
        conversation.last_message = reply[:100]
        await conversation.save()

        # Log usage
        from models.core import UsageLog
        await UsageLog(
            user_id=user_id,
            project="general",
            endpoint="/chat",
            provider=provider,
            model=model_used,
            tokens_used=result.get("tokens_used", 0),
            status="success" if result.get("success") else "error",
        ).insert()

        suggestions = await self._generate_suggestions(message, reply, user_keys)

        return {
            "reply": reply,
            "conversation_id": conversation_id,
            "suggestions": suggestions,
            "tokens_used": result.get("tokens_used", 0),
            "external_data_used": external_data is not None,
            "deep_think_used": deep_think,
            "files_analyzed": files_analyzed,
            "provider": provider,
        }

    # ================================================================================================
    # DYNAMIC SYSTEM PROMPT
    # ================================================================================================

    def _build_dynamic_prompt(
        self,
        interface: str,
        is_new: bool = False,
        has_keys: bool = False,
        context: Optional[str] = None,
    ) -> str:
        """Build a context-aware system prompt that adapts to the conversation."""

        parts = [
            "You are HDM AI, a versatile and intelligent assistant.",
            "You help with general questions, learning, coding, content analysis, business intelligence, and more.",
            "Be warm, natural, and conversational. Adapt your tone to the user's needs.",
            "When appropriate, be concise. When detail is needed, be thorough.",
        ]

        if is_new:
            parts.append(
                "This is the first message in a new conversation. "
                "Start with a friendly greeting that introduces yourself naturally. "
                "Mention you can help with general questions, business insights, coding, learning, and more. "
                "Ask what they'd like to explore today. Keep it warm, not scripted."
            )

        if has_keys:
            parts.append(
                "The user has connected external business systems. "
                "They can ask about their real business data. Suggest relevant queries when appropriate."
            )

        if interface == "mobile":
            parts.append("The user is on mobile. Keep responses concise and easy to read on a small screen.")
        elif interface == "admin":
            parts.append("The user is an administrator. Provide detailed, technical responses.")

        if context:
            parts.append(context)

        return "\n\n".join(parts)

    # ================================================================================================
    # INTENT DETECTION + DATA FETCHING
    # ================================================================================================

    async def _detect_external_intent(self, message: str, user_keys: list) -> dict:
        providers_list = "\n".join([
            f"- {k.provider}: \"{k.name}\" (base_url: {k.base_url or 'not set'})"
            for k in user_keys
        ])
        prompt = f"""Analyze if the user message needs business data from connected systems.

Connected systems:
{providers_list}

User message: "{message}"

Return ONLY valid JSON (no markdown):
{{"needs_external": true/false, "provider": "erp"/"crm"/"database"/"custom" or null, "resource": "products"/"invoices"/"customers"/"sales"/"inventory"/"employees"/"orders" etc., "reason": "short", "query_summary": "5 words"}}
"""
        result = await ai_service.groq_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1, max_tokens=300,
        )
        try:
            text = result.get("reply", "{}").replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except:
            return {"needs_external": False}

    async def _fetch_and_format(self, user_id: str, detection: dict, original_message: str) -> Optional[str]:
        provider = detection.get("provider")
        resource = detection.get("resource", "data")
        if not provider: return None

        key = await ThirdPartyKey.find_one(
            ThirdPartyKey.user_id == user_id,
            ThirdPartyKey.provider == provider,
            ThirdPartyKey.is_active == True,
        )
        if not key: return None

        endpoint = "/"
        if key.api_structure and resource in key.api_structure:
            endpoint = key.api_structure[resource]

        logger.info(f"Fetching external: provider={provider}, resource={resource}, endpoint={endpoint}")

        data = await external_service.fetch_data_for_analysis(user_id, provider, endpoint)
        if not data.get("success"):
            return f"[Note: Failed to fetch {provider} data at {endpoint}: {data.get('error')}]"

        raw = data.get("data", {})
        if isinstance(raw, str) and ("<!DOCTYPE" in raw or "<html" in raw.lower()):
            return f"[Note: {provider} returned HTML. Check your API endpoint URL.]"

        formatted = json.dumps(raw, indent=2) if isinstance(raw, (dict, list)) else str(raw)
        return f"[EXTERNAL DATA - {provider.upper()} at {endpoint}]\n{formatted[:4000]}"

    # ================================================================================================
    # CONVERSATION MANAGEMENT
    # ================================================================================================

    async def get_conversations(self, user_id: str, limit: int = 20) -> List[Dict]:
        conversations = await Conversation.find(
            Conversation.user_id == user_id, Conversation.is_active == True
        ).sort(-Conversation.updated_at).limit(limit).to_list()
        return [
            {"id": str(c.id), "title": c.title, "message_count": c.message_count,
             "last_message": c.last_message, "created_at": c.created_at.isoformat(),
             "updated_at": c.updated_at.isoformat()}
            for c in conversations
        ]

    async def get_messages(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        msgs = await Message.find(Message.conversation_id == conversation_id).sort(+Message.timestamp).limit(limit).to_list()
        return [
            {"id": str(m.id), "role": m.role.value, "content": m.content,
             "tokens_used": m.tokens_used, "timestamp": m.timestamp.isoformat()}
            for m in msgs
        ]

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        conv = await Conversation.get(conversation_id)
        if conv and conv.user_id == user_id:
            await conv.delete()
            for msg in await Message.find(Message.conversation_id == conversation_id).to_list():
                await msg.delete()
            return True
        return False

    async def _generate_suggestions(self, user_msg: str, ai_reply: str, user_keys: list = None) -> List[str]:
        try:
            hint = ""
            if user_keys:
                providers = list(set(k.provider for k in user_keys))
                hint = f" Include 1-2 questions about their {', '.join(providers)} data."
            result = await ai_service.groq_chat(
                messages=[
                    {"role": "system", "content": f"Generate 3 follow-up questions. One per line, no numbers.{hint}"},
                    {"role": "user", "content": f"User: {user_msg}\nAssistant: {ai_reply[:300]}"},
                ],
                temperature=0.8, max_tokens=100,
            )
            if result.get("success"):
                return [s.strip() for s in result["reply"].split("\n") if s.strip()][:3]
        except:
            pass
        return []


chat_service = ChatService()