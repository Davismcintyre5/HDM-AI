# ====================================================================================================
# server/models/erp/alert_schedule.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class AlertSchedule(Document):
    tenant_id: Indexed(str)
    alert_type: str
    message: str
    severity: str = "info"
    scheduled_for: Optional[datetime] = None
    delivered: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "erp_alert_schedules"