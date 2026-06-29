from pydantic import BaseModel
from typing import Optional, List, Dict

class ChatRequest(BaseModel):
    source: str
    message: str
    messages: Optional[List[Dict[str, str]]] = None
    user_id: Optional[str] = None
    context: Optional[Dict] = None
    data: Optional[Dict] = None