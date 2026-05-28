# ====================================================================================================
# 6. server/schemas/spark/privacy.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class PrivacyAdvisorRequest(BaseModel):
    concern: str
    context: Optional[str] = None
    data: Optional[dict] = None

class PrivacyLeakRequest(BaseModel):
    message: str
    scan_type: str = "full"
    data: Optional[dict] = None

class PrivacyEncryptRequest(BaseModel):
    message: str
    recipient_public_key: Optional[str] = None
    data: Optional[dict] = None

class PrivacyAuditRequest(BaseModel):
    user_id: str
    period: str = "last_30d"
    data: Optional[dict] = None