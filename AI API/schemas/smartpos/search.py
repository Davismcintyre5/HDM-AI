# ====================================================================================================
# server/schemas/smartpos/search.py
# ====================================================================================================
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    business_id: str
    query: str
    limit: int = 10

class SearchResponse(BaseModel):
    results: list = []