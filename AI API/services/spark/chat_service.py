from typing import Dict, Any, List, Optional
from services.ai_service import ai_service
import json

class SparkChatService:
    def _build_context(self, message: str, data: Optional[dict] = None) -> str:
        if not data: return ""
        parts = ["\n\nREAL USER DATA:"]
        if "recent_messages" in data:
            parts.append("\nRecent messages:")
            for m in data["recent_messages"][:10]:
                parts.append(f"  • {m.get('from', 'Unknown')}: {m.get('content', '')}")
        if "contacts" in data:
            parts.append(f"\nContacts: {', '.join(data['contacts'][:10])}")
        if "user_preferences" in data:
            parts.append(f"\nPreferences: {json.dumps(data['user_preferences'])}")
        parts.append("\n\nUse this real data to answer accurately. Do not make up information.")
        return "\n".join(parts)

    async def ask(self, user_id: str, message: str, language: str = "en", data: dict = None, feature: str = "private") -> Dict[str, Any]:
        if feature == "public":
            system = "You are Spark Messenger AI, a secure messaging platform. Answer questions about features, privacy, and getting started."
            if data:
                if data.get("features"):
                    system += "\n\nFEATURES:\n" + "\n".join([f"  • {f}" for f in data["features"]])
                if data.get("pricing"):
                    p = data["pricing"]
                    system += f"\n\nPRICING: {p}"
                system += "\n\n⚠️ Use ONLY the above information. Do not invent details. Encourage sign-up."
            system += "\nDo NOT ask the visitor to connect anything."
        else:
            system = "You are Spark Messenger AI. Help with messaging and communication."
            if data:
                system += self._build_context(message, data)
        
        if language != "en": system += f" Respond in {language}."
        
        result = await ai_service.groq_chat([{"role": "system", "content": system}, {"role": "user", "content": message}], max_tokens=800, module="spark")
        return {"reply": result.get("reply", ""), "tokens_used": result.get("tokens_used", 0)}

    async def translate(self, text: str, target_language: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Translate to {target_language}: {text}"}], max_tokens=500, module="spark")
        return {"translated": result.get("reply", text)}

    async def rewrite(self, text: str, style: str = "professional", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Rewrite in {style} style: {text}"}], max_tokens=500, module="spark")
        return {"rewritten": result.get("reply", text)}

    async def draft(self, prompt: str, tone: str = "casual", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Draft a {tone} message: {prompt}"}], max_tokens=500, module="spark")
        return {"draft": result.get("reply", "")}

    async def explain(self, text: str, level: str = "simple", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Explain in {level} terms: {text}"}], max_tokens=500, module="spark")
        return {"explanation": result.get("reply", "")}

    async def summarize(self, text: str, max_length: int = 200, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Summarize in {max_length} chars: {text}"}], max_tokens=300, module="spark")
        return {"summary": result.get("reply", "")}

    async def summarize_unread(self, messages: List[str], data: dict = None) -> Dict[str, Any]:
        text = "\n".join(messages)
        result = await ai_service.groq_chat([{"role": "user", "content": f"Summarize these unread messages:\n{text}"}], max_tokens=500, module="spark")
        return {"unread_summary": result.get("reply", "")}

    async def voice_chat(self, transcript: str, language: str = "en", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "system", "content": f"Respond naturally in {language}."}, {"role": "user", "content": transcript}], max_tokens=500, module="spark")
        return {"response_text": result.get("reply", "")}

    async def emoji_suggest(self, message: str, count: int = 3, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Suggest {count} emojis for: {message}. Return only emojis."}], max_tokens=50, module="spark")
        return {"emojis": result.get("reply", "").strip().split()}

    async def autocomplete(self, partial_text: str, max_suggestions: int = 3, data: dict = None) -> Dict[str, Any]:
        context = ""
        if data and "recent_messages" in data:
            context = f"\nRecent messages:\n" + "\n".join([m.get('content','') for m in data['recent_messages'][:5]])
        result = await ai_service.groq_chat([{"role": "user", "content": f"Complete this message in {max_suggestions} ways:{context}\nText: {partial_text}"}], max_tokens=200, module="spark")
        suggestions = [s.strip() for s in result.get("reply", "").split("\n") if s.strip()]
        return {"suggestions": suggestions[:max_suggestions]}

    async def tone_detect(self, text: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Detect tone. Return one word.\nText: {text}"}], max_tokens=20, module="spark")
        return {"tone": result.get("reply", "neutral").strip()}

    async def format_message(self, text: str, format_type: str = "markdown", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Format in {format_type}: {text}"}], max_tokens=500, module="spark")
        return {"formatted": result.get("reply", text)}

    async def quote_reply(self, original: str, reply: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Original: {original}\nReply: {reply}\nCombine into quoted reply."}], max_tokens=300, module="spark")
        return {"reply": result.get("reply", "")}

    async def poll_generate(self, topic: str, options_count: int = 4, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Create a poll about '{topic}' with {options_count} options. Return JSON: {{question, options:[]}}"}], max_tokens=200, module="spark")
        try: return {"poll": json.loads(result.get("reply", "{}"))}
        except: return {"poll": {"question": topic, "options": [f"Option {i+1}" for i in range(options_count)]}}

    async def context_reply(self, message: str, context_messages: List[str], data: dict = None) -> Dict[str, Any]:
        context = "\n".join(context_messages)
        result = await ai_service.groq_chat([{"role": "user", "content": f"Context:\n{context}\n\nReply to: {message}"}], max_tokens=500, module="spark")
        return {"reply": result.get("reply", "")}

spark_chat_service = SparkChatService()