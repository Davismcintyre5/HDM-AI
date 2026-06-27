from typing import Dict, Any
from services.ai_service import ai_service
import json

class IntelligenceService:
    async def sentiment(self, text: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Analyze sentiment. Return JSON: {{\"sentiment\": \"positive/negative/neutral\", \"score\": -1 to 1}}.\nText: {text}"}], temperature=0.1, max_tokens=100, module="spark")
        try: return {"sentiment": json.loads(result.get("reply", "{}"))}
        except: return {"sentiment": {"sentiment": "neutral", "score": 0}}

    async def keywords(self, text: str, count: int = 10, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Extract top {count} keywords. Return JSON: {{\"keywords\": []}}.\nText: {text}"}], temperature=0.2, max_tokens=200, module="spark")
        try: return {"keywords": json.loads(result.get("reply", "{}")).get("keywords", [])}
        except: return {"keywords": []}

    async def entities(self, text: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Extract named entities. Return JSON: {{\"entities\": [{{\"name\", \"type\"}}]}}.\nText: {text}"}], temperature=0.2, max_tokens=300, module="spark")
        try: return {"entities": json.loads(result.get("reply", "{}")).get("entities", [])}
        except: return {"entities": []}

    async def read_receipt_prediction(self, message: str, sender_history: list = None, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Predict if this message will be read soon. Return JSON: {{\"prediction\": \"likely/neutral/unlikely\"}}.\nMessage: {message}"}], max_tokens=100, module="spark")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"prediction": "neutral"}

    async def urgency(self, message: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Rate urgency. Return JSON: {{\"urgency\": \"low/medium/high\"}}.\nMessage: {message}"}], max_tokens=100, module="spark")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"urgency": "medium"}

    async def language_detect(self, text: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Detect language. Return JSON: {{\"language\": \"en\"}}.\nText: {text}"}], max_tokens=50, module="spark")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"language": "en"}

intelligence_service = IntelligenceService()