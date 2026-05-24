# ====================================================================================================
# server/schemas/vibe/feed.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import List, Optional

class FeedRankRequest(BaseModel):
    user_id: str
    feed_items: List[dict]
    limit: int = 20

class FeedPersonalizeRequest(BaseModel):
    user_id: str
    interests: Optional[List[str]] = None

class FeedTrendingRequest(BaseModel):
    limit: int = 20
    category: Optional[str] = None

class RecommendUsersRequest(BaseModel):
    user_id: str
    limit: int = 10

class RecommendContentRequest(BaseModel):
    user_id: str
    limit: int = 20