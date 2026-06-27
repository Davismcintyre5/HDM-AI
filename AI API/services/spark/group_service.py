from typing import Dict, Any, List
from services.ai_service import ai_service
import json

class GroupService:
    async def summarize(self, messages: List[dict], max_length: int = 300, data: dict = None) -> Dict[str, Any]:
        text = "\n".join([f"{m.get('sender','')}: {m.get('content','')}" for m in messages])
        context = f"\nGroup: {data.get('group_name','')}" if data else ""
        result = await ai_service.groq_chat([{"role": "user", "content": f"Summarize this group chat{context} in {max_length} chars:\n{text}"}], max_tokens=400, module="spark")
        return {"summary": result.get("reply", "")}

    async def highlights(self, messages: List[dict], count: int = 5, data: dict = None) -> Dict[str, Any]:
        text = "\n".join([f"{m.get('sender','')}: {m.get('content','')}" for m in messages])
        result = await ai_service.groq_chat([{"role": "user", "content": f"Extract {count} highlights. Return JSON: {{\"highlights\": []}}.\nChat:\n{text}"}], max_tokens=300, module="spark")
        try: return {"highlights": json.loads(result.get("reply", "{}")).get("highlights", [])}
        except: return {"highlights": []}

    async def poll_results(self, poll_data: dict, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Analyze poll results. Return JSON: {{\"results\": {{}}, \"winner\": \"\"}}.\nData: {poll_data}"}], max_tokens=200, module="spark")
        try: return json.loads(result.get("reply", "{}"))
        except: return {"results": {}}

    async def mention_suggest(self, partial_name: str, group_members: List[str], data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Suggest members matching '{partial_name}' from: {group_members}. Return JSON: {{\"suggestions\": []}}"}], max_tokens=100, module="spark")
        try: return {"suggestions": json.loads(result.get("reply", "{}")).get("suggestions", [])}
        except: return {"suggestions": []}

    async def activity_recap(self, messages: List[dict], period: str = "last_24h", data: dict = None) -> Dict[str, Any]:
        text = "\n".join([f"{m.get('sender','')}: {m.get('content','')}" for m in messages])
        context = f"\nGroup: {data.get('group_name','')} | {data.get('total_messages','?')} msgs | {data.get('active_members','?')} active" if data else ""
        result = await ai_service.groq_chat([{"role": "user", "content": f"Recap group activity for {period}:{context}\n{text}"}], max_tokens=400, module="spark")
        return {"recap": result.get("reply", "")}

group_service = GroupService()