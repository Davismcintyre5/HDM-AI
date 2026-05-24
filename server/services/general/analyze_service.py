"""
HDM AI - General AI Content Analysis Service
Sentiment, summary, keywords, entities, data extraction
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from services.ai_service import ai_service


class AnalyzeService:
    """Content analysis service."""

    VALID_TYPES = ["summary", "sentiment", "keywords", "entities", "data", "full"]

    async def analyze(
        self,
        content: str,
        analysis_type: str = "summary",
    ) -> Dict[str, Any]:
        """Analyze content based on type."""

        if analysis_type not in self.VALID_TYPES:
            return {"success": False, "error": f"Invalid type. Choose: {', '.join(self.VALID_TYPES)}"}

        # Truncate very long content
        max_length = 10000
        if len(content) > max_length:
            content = content[:max_length] + "..."
            logger.warning(f"Content truncated to {max_length} chars")

        try:
            if analysis_type == "summary":
                return await self._summarize(content)
            elif analysis_type == "sentiment":
                return await self._sentiment(content)
            elif analysis_type == "keywords":
                return await self._keywords(content)
            elif analysis_type == "entities":
                return await self._entities(content)
            elif analysis_type == "data":
                return await self._extract_data(content)
            elif analysis_type == "full":
                return await self._full_analysis(content)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def _summarize(self, content: str) -> Dict[str, Any]:
        """Generate a summary."""
        prompt = f"""Summarize the following text in 3-5 sentences. Be concise and capture the main points.

Text:
{content}"""

        result = await ai_service.groq_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )

        return {
            "success": True,
            "result": result.get("reply", ""),
            "analysis_type": "summary",
            "confidence": 0.9,
        }

    async def _sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment."""
        prompt = f"""Analyze the sentiment of this text. Return a JSON object with:
- sentiment: "positive", "negative", or "neutral"
- score: float between -1.0 (very negative) and 1.0 (very positive)
- confidence: float between 0 and 1
- explanation: brief explanation

Text:
{content}"""

        result = await ai_service.groq_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300,
        )

        parsed = self._parse_json(result.get("reply", "{}"))

        return {
            "success": True,
            "result": {
                "sentiment": parsed.get("sentiment", "neutral"),
                "score": parsed.get("score", 0.0),
                "confidence": parsed.get("confidence", 0.5),
                "explanation": parsed.get("explanation", ""),
            },
            "analysis_type": "sentiment",
        }

    async def _keywords(self, content: str) -> Dict[str, Any]:
        """Extract keywords."""
        prompt = f"""Extract the top 10 most important keywords or key phrases from this text.
Return as JSON: {{"keywords": ["keyword1", "keyword2", ...]}}

Text:
{content}"""

        result = await ai_service.groq_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )

        parsed = self._parse_json(result.get("reply", "{}"))

        return {
            "success": True,
            "result": parsed.get("keywords", []),
            "analysis_type": "keywords",
            "confidence": 0.85,
        }

    async def _entities(self, content: str) -> Dict[str, Any]:
        """Extract named entities."""
        prompt = f"""Extract named entities from this text. Categorize as: person, organization, location, date, product, event.
Return as JSON: {{"entities": [{{"name": "...", "type": "...", "context": "..."}}]}}

Text:
{content}"""

        result = await ai_service.groq_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500,
        )

        parsed = self._parse_json(result.get("reply", "{}"))

        return {
            "success": True,
            "result": parsed.get("entities", []),
            "analysis_type": "entities",
            "confidence": 0.8,
        }

    async def _extract_data(self, content: str) -> Dict[str, Any]:
        """Extract structured data."""
        prompt = f"""Extract structured data from this text. Identify any tables, lists, numbers, dates, prices, or structured information.
Return as JSON with appropriate keys based on the content.

Text:
{content}"""

        result = await ai_service.groq_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
        )

        parsed = self._parse_json(result.get("reply", "{}"))

        return {
            "success": True,
            "result": parsed,
            "analysis_type": "data",
            "confidence": 0.75,
        }

    async def _full_analysis(self, content: str) -> Dict[str, Any]:
        """Run all analysis types."""
        summary_result = await self._summarize(content)
        sentiment_result = await self._sentiment(content)
        keywords_result = await self._keywords(content)

        return {
            "success": True,
            "result": {
                "summary": summary_result.get("result", ""),
                "sentiment": sentiment_result.get("result", {}),
                "keywords": keywords_result.get("result", []),
            },
            "analysis_type": "full",
            "confidence": 0.85,
        }

    def _parse_json(self, text: str) -> dict:
        """Parse JSON from AI response, handling markdown code blocks."""
        import json
        import re

        # Remove markdown code blocks
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "").strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return {}


analyze_service = AnalyzeService()