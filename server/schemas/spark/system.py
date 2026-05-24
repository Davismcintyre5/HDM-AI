# ====================================================================================================
# server/schemas/spark/system.py
# ====================================================================================================
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"

class StatsResponse(BaseModel):
    requests_today: int = 0
    total_requests: int = 0
    active_users: int = 0