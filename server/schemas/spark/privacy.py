# ====================================================================================================
# server/schemas/spark/privacy.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class PrivacyAdvisorRequest(BaseModel):
    concern: str
    context: Optional[str] = None

class PrivacyLeakRequest(BaseModel):
    message: str
    scan_type: str = "full"  # full, quick

class PrivacyEncryptRequest(BaseModel):
    message: str
    recipient_public_key: Optional[str] = None

class PrivacyAuditRequest(BaseModel):
    user_id: str
    period: str = "last_30d"