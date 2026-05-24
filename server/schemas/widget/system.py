# ====================================================================================================
# server/schemas/widget/system.py
# ====================================================================================================
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str = "healthy"
    source: str = "widget_ai"