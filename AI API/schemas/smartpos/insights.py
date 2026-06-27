# ====================================================================================================
# server/schemas/smartpos/insights.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class InsightsRequest(BaseModel):
    business_id: str
    insight_type: str
    data: Optional[dict] = None

class InsightsResponse(BaseModel):
    type: str
    data: dict = {}
    summary: str = ""