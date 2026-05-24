# ====================================================================================================
# server/schemas/smartpos/chat.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    client_id: str
    business_id: Optional[str] = None
    feature: str = "chat"  # chat, public
    data: Optional[dict] = None  # REAL inventory, sales, product data

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    tokens_used: int = 0