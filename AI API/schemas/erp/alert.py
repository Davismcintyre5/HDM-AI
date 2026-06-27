# ====================================================================================================
# server/schemas/erp/alert.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional, List

class AlertAnalyzeRequest(BaseModel):
    tenant_id: str
    data: dict = {}

class AlertAnalyzeResponse(BaseModel):
    alerts: List[dict] = []
    severity: str = "low"