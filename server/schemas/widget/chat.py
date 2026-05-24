# ====================================================================================================
# server/schemas/widget/chat.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    source: str = Field(..., pattern="^(docusoft|hdm_portfolio)$")
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    source: str
    tokens_used: int = 0