# ====================================================================================================
# server/models/erp/usage_log.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class ERPUsageLog(Document):
    tenant_id: Indexed(str)
    endpoint: str
    provider: str = "groq"
    model: str = ""
    tokens_used: int = 0
    response_time_ms: float = 0
    status: str = "success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "erp_usage_logs"