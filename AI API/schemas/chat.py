from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=10000)
    messages: Optional[List[Dict[str, str]]] = None
    provider: Optional[str] = "groq"
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096
    system_prompt: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    search_enabled: Optional[bool] = False
    deep_think: Optional[bool] = False