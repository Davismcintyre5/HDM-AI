# ====================================================================================================
# 2. server/schemas/vault/security.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional, List

class SecurityOverviewRequest(BaseModel):
    user_id: str
    include_details: bool = True
    data: Optional[dict] = None  # password_health, breaches, devices, network

class SecurityAlertRequest(BaseModel):
    user_id: str
    severity_filter: Optional[str] = None  # info, warning, critical
    data: Optional[dict] = None  # current_threats