# ====================================================================================================
# 7. server/schemas/vibe/analytics.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class EngagementRequest(BaseModel):
    user_id: str
    period: str = "last_30d"
    data: Optional[dict] = None

class ChurnRequest(BaseModel):
    user_id: str
    activity_data: Optional[dict] = None
    data: Optional[dict] = None

class GrowthRequest(BaseModel):
    user_id: str
    metrics: Optional[dict] = None
    data: Optional[dict] = None