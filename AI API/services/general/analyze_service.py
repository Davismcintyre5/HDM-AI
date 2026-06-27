from typing import Dict, Any
from services.ai_service import ai_service
from loguru import logger
import json

class AnalyzeService:
    VALID_TYPES = ["summary", "sentiment", "keywords", "entities", "data", "full"]

    async def analyze(self, content: str, analysis_type: str = "summary") -> Dict[str, Any]:
        if analysis_type not in self.VALID_TYPES:
            return {"success": False, "error": f"Invalid type. Choose: {', '.join(self.VALID_TYPES)}"}
        if len(content) > 10000:
            content = content[:10000] + "..."
        try:
            if analysis_type == "summary": return await self._summarize(content)
            elif analysis_type == "sentiment": return await self._sentiment(content)
            elif analysis_type == "keywords": return await self._keywords(content)
            elif analysis_type == "entities": return await self._entities(content)
            elif analysis_type == "data": return await self._extract_data(content)
            elif analysis_type == "full": return await self._full_analysis(content)
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _summarize(self, content: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Summarize in 3-5 sentences:\n{content}"}], temperature=0.3, max_tokens=500, module="general")
        return {"success": True, "result": result.get("reply", ""), "analysis_type": "summary", "confidence": 0.9}

    async def _sentiment(self, content: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Analyze sentiment. Return JSON: {{\"sentiment\": \"positive/negative/neutral\", \"score\": -1 to 1, \"confidence\": 0.0-1.0, \"explanation\": \"...\"}}.\nText: {content}"}], temperature=0.1, max_tokens=300, module="general")
        try:
            return {"success": True, "result": json.loads(result.get("reply", "{}")), "analysis_type": "sentiment"}
        except:
            return {"success": True, "result": {"sentiment": "neutral", "score": 0}, "analysis_type": "sentiment"}

    async def _keywords(self, content: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Extract top 10 keywords as JSON: {{\"keywords\": []}}.\nText: {content}"}], temperature=0.3, max_tokens=300, module="general")
        try:
            return {"success": True, "result": json.loads(result.get("reply", "{}")).get("keywords", []), "analysis_type": "keywords"}
        except:
            return {"success": True, "result": [], "analysis_type": "keywords"}

    async def _entities(self, content: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Extract named entities as JSON: {{\"entities\": [{{\"name\": \"...\", \"type\": \"...\"}}]}}.\nText: {content}"}], temperature=0.2, max_tokens=500, module="general")
        try:
            return {"success": True, "result": json.loads(result.get("reply", "{}")).get("entities", []), "analysis_type": "entities"}
        except:
            return {"success": True, "result": [], "analysis_type": "entities"}

    async def _extract_data(self, content: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat([{"role": "user", "content": f"Extract structured data as JSON.\nText: {content}"}], temperature=0.2, max_tokens=1000, module="general")
        try:
            return {"success": True, "result": json.loads(result.get("reply", "{}")), "analysis_type": "data"}
        except:
            return {"success": True, "result": {}, "analysis_type": "data"}

    async def _full_analysis(self, content: str) -> Dict[str, Any]:
        summary = await self._summarize(content)
        sentiment = await self._sentiment(content)
        keywords = await self._keywords(content)
        return {"success": True, "result": {"summary": summary.get("result", ""), "sentiment": sentiment.get("result", {}), "keywords": keywords.get("result", [])}, "analysis_type": "full"}

analyze_service = AnalyzeService()