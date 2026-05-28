# ====================================================================================================
# 2. server/schemas/spark/smart_reply.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class SmartReplyRequest(BaseModel):
    message: str
    count: int = 3
    tone: Optional[str] = None
    data: Optional[dict] = None

class SmartQuickReplyRequest(BaseModel):
    message: str
    count: int = 4
    data: Optional[dict] = None

class SmartReplyContextRequest(BaseModel):
    message: str
    previous_messages: list = []
    data: Optional[dict] = None

class SmartReplyToneRequest(BaseModel):
    message: str
    target_tone: str = "friendly"
    data: Optional[dict] = None

class SmartReplyLanguageRequest(BaseModel):
    message: str
    language: str = "en"
    data: Optional[dict] = None