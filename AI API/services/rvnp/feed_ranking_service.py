from services.ai_service import ai_service
import json

class FeedRankingService:
    async def rank(self, posts: list, userInterests: list = None, userDepartment: str = None, userHostel: str = None) -> dict:
        posts_json = json.dumps(posts, indent=2)[:4000]
        prompt = f"""Rank these posts by relevance to the user.
User interests: {userInterests or []}
User department: {userDepartment or 'N/A'}
User hostel: {userHostel or 'N/A'}

Posts:
{posts_json}

Return JSON: {{"rankedPosts": [{{"_id": "...", "relevanceScore": 0.0-1.0, "rankingFactors": {{"interestMatch": 0.0, "departmentMatch": 0.0, "freshness": 0.0, "engagement": 0.0, "verifiedAuthor": 0.0}}}}]}}"""

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=800, module="rvnp")
        try:
            return json.loads(result.get("reply", "{}"))
        except:
            return {"rankedPosts": [{"_id": p.get("_id"), "relevanceScore": 0.5, "rankingFactors": {}} for p in posts]}

feed_ranking_service = FeedRankingService()