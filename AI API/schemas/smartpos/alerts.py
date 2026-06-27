# ====================================================================================================
# server/schemas/smartpos/alerts.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class AlertCheckRequest(BaseModel):
    business_id: str
    data: Optional[dict] = None
    alert_types: Optional[list] = None

class AlertCheckResponse(BaseModel):
    alerts: list = []
    has_critical: bool = False