# ====================================================================================================
# 4. server/schemas/spark/moderation.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class SafetySpamRequest(BaseModel):
    text: str
    user_id: Optional[str] = None
    data: Optional[dict] = None

class SafetyHateRequest(BaseModel):
    text: str
    data: Optional[dict] = None

class SafetyNSFWRequest(BaseModel):
    content: str
    content_type: str = "text"
    data: Optional[dict] = None

class SafetyChildRequest(BaseModel):
    content: str
    user_age: Optional[int] = None
    data: Optional[dict] = None

class SafetyImpersonationRequest(BaseModel):
    text: str
    claimed_identity: Optional[str] = None
    data: Optional[dict] = None

class SafetySelfHarmRequest(BaseModel):
    text: str
    user_id: Optional[str] = None
    data: Optional[dict] = None

class SafetyLinkRequest(BaseModel):
    url: str
    data: Optional[dict] = None