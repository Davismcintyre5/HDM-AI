# ====================================================================================================
# server/models/smartpos/alert.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class Alert(Document):
    business_id: Indexed(str)
    type: str  # low_stock, unusual_activity, etc.
    message: str
    severity: str = "info"  # info, warning, critical
    acknowledged: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "smartpos_alerts"