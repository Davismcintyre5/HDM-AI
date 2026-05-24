# ====================================================================================================
# server/schemas/spark/search.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import List, Optional

class SemanticSearchRequest(BaseModel):
    query: str
    documents: Optional[List[dict]] = None
    limit: int = 10

class MessageSearchRequest(BaseModel):
    query: str
    user_id: str
    limit: int = 20

class ContactSearchRequest(BaseModel):
    query: str
    user_id: str
    limit: int = 10