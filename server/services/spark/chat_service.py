# ====================================================================================================
# server/services/spark/chat_service.py
# ====================================================================================================
from typing import Dict, Any, List, Optional
from services.ai_service import ai_service
from loguru import logger

class SparkChatService:
    async def ask(self, user_id: str, message: str, language: str = "en") -> Dict[str, Any]:
        system = "You are Spark Messenger AI. Help with messaging, communication, and productivity. Be friendly and concise."
        if language != "en": system += f" Respond in {language}."
        result = await ai_service.groq_chat([{"role": "system", "content": system}, {"role": "user", "content": message}], max_tokens=800)
        return {"reply": result.get("reply", ""), "tokens_used": result.get("tokens_used", 0)}

    async def translate(self, text: str, target_language: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Translate to {target_language}: {text}"}], max_tokens=500)
        return {"translated": result.get("reply", text)}

    async def rewrite(self, text: str, style: str = "professional") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Rewrite in {style} style: {text}"}], max_tokens=500)
        return {"rewritten": result.get("reply", text)}

    async def draft(self, prompt: str, tone: str = "casual") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Draft a {tone} message: {prompt}"}], max_tokens=500)
        return {"draft": result.get("reply", "")}

    async def explain(self, text: str, level: str = "simple") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Explain in {level} terms: {text}"}], max_tokens=500)
        return {"explanation": result.get("reply", "")}

    async def summarize(self, text: str, max_length: int = 200) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Summarize in {max_length} characters: {text}"}], max_tokens=300)
        return {"summary": result.get("reply", "")}

    async def summarize_unread(self, messages: List[str]) -> Dict[str, Any]:
        text = "\n".join(messages)
        result = await ai_service.groq_chat([{"role": "user", "content": f"Summarize these unread messages: {text}"}], max_tokens=500)
        return {"unread_summary": result.get("reply", "")}

    async def voice_chat(self, transcript: str, language: str = "en") -> Dict[str, Any]:
        system = f"You are a voice assistant. Respond naturally in {language}."
        result = await ai_service.groq_chat([{"role": "system", "content": system}, {"role": "user", "content": transcript}], max_tokens=500)
        return {"audio_url": "", "response_text": result.get("reply", "")}

    async def emoji_suggest(self, message: str, count: int = 3) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Suggest {count} relevant emojis for: {message}. Return only emojis."}], max_tokens=50)
        return {"emojis": result.get("reply", "").strip().split()}

    async def autocomplete(self, partial_text: str, max_suggestions: int = 3) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Complete this message in {max_suggestions} ways: {partial_text}"}], max_tokens=200)
        suggestions = [s.strip() for s in result.get("reply", "").split("\n") if s.strip()]
        return {"suggestions": suggestions[:max_suggestions]}

    async def tone_detect(self, text: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Detect the tone: {text}. Return one word."}], max_tokens=20)
        return {"tone": result.get("reply", "neutral").strip()}

    async def format_message(self, text: str, format_type: str = "markdown") -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Format this in {format_type}: {text}"}], max_tokens=500)
        return {"formatted": result.get("reply", text)}

    async def quote_reply(self, original: str, reply: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Original: {original}\nReply: {reply}\nCombine into a quoted reply."}], max_tokens=300)
        return {"reply": result.get("reply", "")}

    async def poll_generate(self, topic: str, options_count: int = 4) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Create a poll about '{topic}' with {options_count} options. Return as JSON: {{question, options:[]}}"}], max_tokens=200)
        try:
            import json
            return {"poll": json.loads(result.get("reply", "{}"))}
        except:
            return {"poll": {"question": topic, "options": [f"Option {i+1}" for i in range(options_count)]}}

    async def context_reply(self, message: str, context_messages: List[str]) -> Dict[str, Any]:
        context = "\n".join(context_messages)
        result = await ai_service.groq_chat([{"role": "user", "content": f"Context:\n{context}\n\nReply to: {message}"}], max_tokens=500)
        return {"reply": result.get("reply", "")}

spark_chat_service = SparkChatService()