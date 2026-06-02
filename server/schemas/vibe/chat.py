# ====================================================================================================
# 2. server/schemas/vibe/chat.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class ChatMessageRequest(BaseModel):
    user_id: str
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    data: Optional[dict] = None

class ChatAssistantRequest(BaseModel):
    user_id: str
    task: str
    context: Optional[dict] = None
    data: Optional[dict] = None

class ChatCreativeRequest(BaseModel):
    user_id: str
    prompt: str
    style: Optional[str] = None
    data: Optional[dict] = None