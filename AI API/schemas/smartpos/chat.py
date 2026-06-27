from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_id: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    conversation_id: Optional[str] = None
    client_id: str
    business_id: Optional[str] = None
    feature: str = "chat"
    data: Optional[dict] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    tokens_used: int = 0