from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    user_id: str
    feature: str = "public"
    data: Optional[dict] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    tokens_used: int = 0