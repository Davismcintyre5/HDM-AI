# ====================================================================================================
# 11. server/services/spark/moderation_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.spark.moderation_log import ModerationLog
from models.spark.safety_incident import SafetyIncident
import json

class ModerationService:
    async def check_spam(self, text: str, user_id: str = None, data: dict = None) -> Dict[str, Any]:
        context = ""
        if data and "user_history" in data:
            h = data["user_history"]
            context = f"\nUser history: {h.get('messages_sent_today',0)} msgs today, account age: {h.get('account_age_days',0)} days"
        result = await ai_service.groq_chat([{"role": "user", "content": f"Is this spam?{context}\nReturn JSON: {{\"is_spam\": true/false, \"confidence\": 0.0-1.0}}.\nText: {text}"}], temperature=0.1, max_tokens=80)
        try:
            data = json.loads(result.get("reply", "{}"))
            await ModerationLog(user_id=user_id, content_type="text", flagged=data.get("is_spam", False), category="spam", confidence=data.get("confidence", 0)).insert()
            return data
        except: return {"is_spam": False}

    async def check_hate_speech(self, text: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Does this contain hate speech? Return JSON: {{\"flagged\": true/false}}.\nText: {text}"}], temperature=0.1, max_tokens=80)
        try: return json.loads(result.get("reply", "{}"))
        except: return {"flagged": False}

    async def check_nsfw(self, content: str, content_type: str = "text", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Is this NSFW? Return JSON: {{\"is_nsfw\": true/false}}.\nContent: {content}"}], temperature=0.1, max_tokens=80)
        try: return json.loads(result.get("reply", "{}"))
        except: return {"is_nsfw": False}

    async def check_child_safety(self, content: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Is this content safe for children? Return JSON: {{\"flagged\": true/false}}.\nContent: {content}"}], temperature=0.1, max_tokens=100)
        try: return json.loads(result.get("reply", "{}"))
        except: return {"flagged": False}

    async def check_impersonation(self, text: str, claimed_identity: str = None, data: dict = None) -> Dict[str, Any]:
        context = ""
        if data:
            context = f"\nActual user: {data.get('actual_user_name','Unknown')} ({data.get('actual_user_role','unknown')})"
        result = await ai_service.groq_chat([{"role": "user", "content": f"Is this impersonation?{context}\nReturn JSON: {{\"detected\": true/false}}.\nText: {text}"}], temperature=0.1, max_tokens=50)
        try: return json.loads(result.get("reply", "{}"))
        except: return {"detected": False}

    async def check_self_harm(self, text: str, user_id: str = None, data: dict = None) -> Dict[str, Any]:
        context = ""
        if data and "recent_messages" in data:
            context = f"\nRecent messages: {'; '.join(data['recent_messages'][:3])}"
        location = data.get("user_location", "") if data else ""
        result = await ai_service.groq_chat([{"role": "user", "content": f"Does this indicate self-harm?{context}\nLocation: {location}\nReturn JSON: {{\"detected\": true/false, \"resources\": [\"crisis line\"]}}.\nText: {text}"}], temperature=0.1, max_tokens=150)
        try:
            data = json.loads(result.get("reply", "{}"))
            if data.get("detected"):
                await SafetyIncident(user_id=user_id, severity="critical", incident_type="self_harm", description=text, resources_provided=data.get("resources", [])).insert()
            return data
        except: return {"detected": False, "resources": []}

    async def check_link(self, url: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Is this link malicious? Return JSON: {{\"is_malicious\": true/false}}.\nURL: {url}"}], temperature=0.1, max_tokens=50)
        try: return json.loads(result.get("reply", "{}"))
        except: return {"is_malicious": False}

moderation_service = ModerationService()