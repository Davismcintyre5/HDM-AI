# ====================================================================================================
# server/schemas/smartpos/forecast.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class ForecastRequest(BaseModel):
    business_id: str
    forecast_type: str
    period: Optional[str] = "next_month"
    data: Optional[dict] = None
    product_ids: Optional[list] = None

class ForecastResponse(BaseModel):
    type: str
    forecast: list = []
    summary: str = ""