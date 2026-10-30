from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class LearnChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=10000)
    messages: Optional[List[Dict[str, str]]] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.5
    max_tokens: Optional[int] = 4096
    data: Optional[Dict[str, Any]] = None