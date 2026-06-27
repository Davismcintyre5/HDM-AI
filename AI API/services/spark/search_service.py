from typing import Dict, Any, List
from services.ai_service import ai_service
import json

class SparkSearchService:
    async def semantic_search(self, query: str, documents: List[dict] = None, limit: int = 10, data: dict = None) -> Dict[str, Any]:
        docs_json = json.dumps(documents)[:3000] if documents else "[]"
        result = await ai_service.groq_chat([{"role": "user", "content": f"Find top {limit} results for '{query}' from: {docs_json}. Return JSON: {{\"results\": []}}"}], max_tokens=500, module="spark")
        try: return {"results": json.loads(result.get("reply", "{}")).get("results", [])}
        except: return {"results": []}

    async def message_search(self, query: str, user_id: str, limit: int = 20, data: dict = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Search messages for '{query}'. Return JSON: {{\"messages\": []}}"}], max_tokens=300, module="spark")
        try: return {"messages": json.loads(result.get("reply", "{}")).get("messages", [])}
        except: return {"messages": []}

    async def contact_search(self, query: str, user_id: str, limit: int = 10, data: dict = None) -> Dict[str, Any]:
        context = ""
        if data and "frequent_contacts" in data:
            context = f"\nFrequent contacts: {', '.join(data['frequent_contacts'])}"
        result = await ai_service.groq_chat([{"role": "user", "content": f"Search contacts for '{query}'.{context}\nReturn JSON: {{\"contacts\": []}}"}], max_tokens=200, module="spark")
        try: return {"contacts": json.loads(result.get("reply", "{}")).get("contacts", [])}
        except: return {"contacts": []}

spark_search_service = SparkSearchService()