# ====================================================================================================
# 1. server/schemas/vault/chat.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    user_id: str
    feature: str = "public"  # public, private
    data: Optional[dict] = None  # real user security data