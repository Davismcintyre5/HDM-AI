# ====================================================================================================
# server/schemas/spark/moderation.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class SafetySpamRequest(BaseModel):
    text: str
    user_id: Optional[str] = None

class SafetyHateRequest(BaseModel):
    text: str

class SafetyNSFWRequest(BaseModel):
    content: str  # text or image description
    content_type: str = "text"

class SafetyChildRequest(BaseModel):
    content: str
    user_age: Optional[int] = None

class SafetyImpersonationRequest(BaseModel):
    text: str
    claimed_identity: Optional[str] = None

class SafetySelfHarmRequest(BaseModel):
    text: str
    user_id: Optional[str] = None

class SafetyLinkRequest(BaseModel):
    url: str