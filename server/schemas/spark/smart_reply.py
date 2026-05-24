# ====================================================================================================
# server/schemas/spark/smart_reply.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class SmartReplyRequest(BaseModel):
    message: str
    count: int = 3
    tone: Optional[str] = None

class SmartQuickReplyRequest(BaseModel):
    message: str
    count: int = 4

class SmartReplyContextRequest(BaseModel):
    message: str
    previous_messages: list = []

class SmartReplyToneRequest(BaseModel):
    message: str
    target_tone: str = "friendly"

class SmartReplyLanguageRequest(BaseModel):
    message: str
    language: str = "en"