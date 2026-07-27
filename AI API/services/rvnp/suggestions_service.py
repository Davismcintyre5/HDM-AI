from services.ai_service import ai_service
import json

class SuggestionsService:
    async def suggest(self, lastMessages: list, chatType: str = "direct", relationship: str = "classmate") -> dict:
        context = "\n".join([f"{m.get('sender')}: {m.get('content')}" for m in lastMessages[-5:]])
        prompt = f"""Generate 4 short reply suggestions for this chat.
Chat type: {chatType}
Relationship: {relationship}

Conversation:
{context}

Return JSON: {{"suggestions": ["reply1", "reply2", "reply3", "reply4"]}}"""

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.7, max_tokens=150, module="rvnp")
        try:
            return json.loads(result.get("reply", "{}"))
        except:
            return {"suggestions": ["I'll be there!", "See you soon", "Can't make it", "Let me check"]}

suggestions_service = SuggestionsService()