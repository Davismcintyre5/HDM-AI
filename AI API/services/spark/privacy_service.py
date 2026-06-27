from typing import Dict, Any
from services.ai_service import ai_service
import json

class PrivacyService:
    async def advisor(self, concern: str, context: str = None, data: dict = None) -> Dict[str, Any]:
        prompt = f"Give privacy advice about: {concern}"
        if context: prompt += f"\nContext: {context}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=500, module="spark")
        return {"advice": result.get("reply", "")}

    async def data_leak_check(self, message: str, scan_type: str = "full", data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Check for data leaks (emails, phones, SSN, credit cards, keys). Return JSON: {{\"detected\": true/false, \"findings\": []}}.\nText: {message}"}], temperature=0.1, max_tokens=200, module="spark")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"detected": False, "findings": []}

    async def encrypt_suggest(self, message: str, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Suggest encryption for this message. Return JSON: {{\"suggestion\": \"...\"}}.\nMessage: {message}"}], max_tokens=100, module="spark")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"suggestion": "Use end-to-end encryption"}

    async def audit_log(self, user_id: str, period: str = "last_30d", data: dict = None) -> Dict[str, Any]:
        data_json = json.dumps(data)[:2000] if data else "{}"
        result = await ai_service.groq_chat([{"role": "user", "content": f"Generate privacy audit for user {user_id} for {period}. Data: {data_json}\nReturn JSON: {{\"log\": []}}"}], max_tokens=300, module="spark")
        try: return {"log": json.loads(result.get("reply", "{}")).get("log", [])}
        except: return {"log": []}

privacy_service = PrivacyService()