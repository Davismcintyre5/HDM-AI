# ====================================================================================================
# HDM AI Engine — Analyze Service (/v1/analyze)
# Content analysis | Key 1
# ====================================================================================================

import json
from typing import Dict, Any
from services.ai_service import ai_service


class AnalyzeService:
    VALID = ["summary", "sentiment", "keywords", "entities", "data", "full"]

    async def analyze(self, user_id: str, content: str, analysis_type: str = "summary") -> Dict[str, Any]:
        if analysis_type not in self.VALID:
            return {"success": False, "error": f"Invalid type. Choose: {', '.join(self.VALID)}"}
        if len(content) > 10000:
            content = content[:10000] + "..."

        try:
            if analysis_type == "summary":
                return await self._text(content, "Summarize in 3-5 sentences:", "summary")
            if analysis_type == "sentiment":
                return await self._json(content, 'Analyze sentiment. Return JSON: {"sentiment": "positive/negative/neutral", "score": -1 to 1, "explanation": "..."}', "sentiment")
            if analysis_type == "keywords":
                return await self._json(content, 'Extract top 10 keywords. Return JSON: {"keywords": []}', "keywords", "keywords")
            if analysis_type == "entities":
                return await self._json(content, 'Extract named entities. Return JSON: {"entities": [{"name": "...", "type": "..."}]}', "entities", "entities")
            if analysis_type == "data":
                return await self._json(content, "Extract structured data as JSON.", "data")
            if analysis_type == "full":
                return await self._full(content)
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _text(self, content: str, instruction: str, t: str) -> Dict[str, Any]:
        result = await ai_service.groq_chat(
            [{"role": "user", "content": f"{instruction}\n{content}"}],
            bucket="chat", temperature=0.3, max_tokens=500,
        )
        return {"success": True, "result": result.get("reply", ""), "analysis_type": t}

    async def _json(self, content: str, instruction: str, t: str, key: str = None) -> Dict[str, Any]:
        result = await ai_service.groq_chat(
            [{"role": "user", "content": f"{instruction}\nText: {content}"}],
            bucket="chat", temperature=0.2, max_tokens=500,
        )
        try:
            data = json.loads(result.get("reply", "{}"))
            return {"success": True, "result": data.get(key, data) if key else data, "analysis_type": t}
        except Exception:
            return {"success": True, "result": {}, "analysis_type": t}

    async def _full(self, content: str) -> Dict[str, Any]:
        summary = await self._text(content, "Summarize in 3-5 sentences:", "summary")
        sentiment = await self._json(content, 'Analyze sentiment. Return JSON: {"sentiment": "...", "score": 0}', "sentiment")
        keywords = await self._json(content, 'Extract top 10 keywords. Return JSON: {"keywords": []}', "keywords", "keywords")
        return {
            "success": True,
            "result": {
                "summary": summary.get("result", ""),
                "sentiment": sentiment.get("result", {}),
                "keywords": keywords.get("result", []),
            },
            "analysis_type": "full",
        }


analyze_service = AnalyzeService()