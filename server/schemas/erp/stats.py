# ====================================================================================================
# server/schemas/erp/stats.py
# ====================================================================================================
from pydantic import BaseModel

class StatsResponse(BaseModel):
    total_requests: int = 0
    tokens_used: int = 0
    tenants: list = []