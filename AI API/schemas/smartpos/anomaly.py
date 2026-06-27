# ====================================================================================================
# server/schemas/smartpos/anomaly.py
# ====================================================================================================
from pydantic import BaseModel, Field

class AnomalyRequest(BaseModel):
    business_id: str
    data: list = []

class AnomalyResponse(BaseModel):
    anomalies: list = []
    count: int = 0