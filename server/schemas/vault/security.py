from pydantic import BaseModel, Field
from typing import Optional, List

class SecurityOverviewRequest(BaseModel):
    user_id: str
    include_details: bool = True
    data: Optional[dict] = None

class SecurityAlertRequest(BaseModel):
    user_id: str
    severity_filter: Optional[str] = None
    data: Optional[dict] = None

class SecurityOverviewResponse(BaseModel):
    score: int = 0
    summary: str = ""
    findings: List[dict] = []
    recommendations: List[str] = []

class SecurityAlertResponse(BaseModel):
    alerts: List[dict] = []
    has_critical: bool = False