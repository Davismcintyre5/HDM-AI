# ====================================================================================================
# server/schemas/vault/security.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional, List

class SecurityOverviewRequest(BaseModel):
    user_id: str
    include_details: bool = True

class SecurityAlertRequest(BaseModel):
    user_id: str
    severity_filter: Optional[str] = None  # info, warning, critical

class SecurityOverviewResponse(BaseModel):
    score: int = 0
    summary: str = ""
    findings: List[dict] = []
    recommendations: List[str] = []

class SecurityAlertResponse(BaseModel):
    alerts: List[dict] = []
    has_critical: bool = False