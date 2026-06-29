from pydantic import BaseModel, Field
from typing import Optional

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    tenant_id: Optional[str] = "public"
    provider: Optional[str] = "groq"
    context: Optional[dict] = {}
    data: Optional[dict] = None

class QueryResponse(BaseModel):
    reply: str
    provider: str
    tokens_used: int = 0
    data_analyzed: bool = False