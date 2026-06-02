# ====================================================================================================
# 6. server/schemas/vibe/monetization.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class AdTargetRequest(BaseModel):
    campaign_goal: str
    budget: Optional[float] = None
    audience: Optional[dict] = None
    data: Optional[dict] = None

class AdCopyRequest(BaseModel):
    product: str
    target_audience: str
    platform: str = "instagram"
    data: Optional[dict] = None

class PriceSuggestRequest(BaseModel):
    product: str
    category: str
    market_data: Optional[dict] = None
    data: Optional[dict] = None

class SponsorMatchRequest(BaseModel):
    creator_profile: dict
    niche: str
    data: Optional[dict] = None