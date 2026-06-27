# ====================================================================================================
# server/schemas/smartpos/admin.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class AdminChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class AdminChatResponse(BaseModel):
    reply: str
    conversation_id: str