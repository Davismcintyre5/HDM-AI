# ====================================================================================================
# server/services/spark/group_service.py
# ====================================================================================================
from typing import Dict, Any, List
from services.ai_service import ai_service
import json

class GroupService:
    async def summarize(self, messages: List[dict], max_length: int = 300) -> Dict[str, Any]:
        text = "\n".join([f"{m.get('sender','')}: {m.get('content','')}" for m in messages])
        result = await ai_service.groq_chat([{"role": "user", "content": f"Summarize this group chat in {max_length} chars:\n{text}"}], max_tokens=400)
        return {"summary": result.get("reply", "")}

    async def highlights(self, messages: List[dict], count: int = 5) -> Dict[str, Any]:
        text = "\n".join([f"{m.get('sender','')}: {m.get('content','')}" for m in messages])
        result = await ai_service.groq_chat([{"role": "user", "content": f"Extract {count} highlights. Return JSON: {{\"highlights\": []}}.\nChat:\n{text}"}], max_tokens=300)
        try: return {"highlights": json.loads(result.get("reply", "{}")).get("highlights", [])}
        except: return {"highlights": []}

    async def poll_results(self, poll_data: dict) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Analyze poll results. Return JSON: {{\"results\": {{}}, \"winner\": \"\"}}.\nData: {poll_data}"}], max_tokens=200)
        try: return json.loads(result.get("reply", "{}"))
        except: return {"results": {}}

    async def mention_suggest(self, partial_name: str, group_members: List[str]) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Suggest members matching '{partial_name}' from: {group_members}. Return JSON: {{\"suggestions\": []}}"}], max_tokens=100)
        try: return {"suggestions": json.loads(result.get("reply", "{}")).get("suggestions", [])}
        except: return {"suggestions": []}

    async def activity_recap(self, messages: List[dict], period: str = "last_24h") -> Dict[str, Any]:
        text = "\n".join([f"{m.get('sender','')}: {m.get('content','')}" for m in messages])
        result = await ai_service.groq_chat([{"role": "user", "content": f"Recap group activity for {period}:\n{text}"}], max_tokens=400)
        return {"recap": result.get("reply", "")}

group_service = GroupService()