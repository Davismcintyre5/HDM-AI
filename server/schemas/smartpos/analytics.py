# ====================================================================================================
# server/schemas/smartpos/analytics.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class AnalyticsRequest(BaseModel):
    business_id: str
    analytics_type: str
    period: Optional[str] = "this_month"
    data: Optional[dict] = None
    filters: Optional[dict] = {}

class AnalyticsResponse(BaseModel):
    type: str
    data: dict = {}
    summary: str = ""