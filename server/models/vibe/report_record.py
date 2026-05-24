# ====================================================================================================
# server/models/vibe/report_record.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class ReportRecord(Document):
    reporter_id: Indexed(str)
    content_id: str
    reason: str
    status: str = "pending"  # pending, reviewed, resolved
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "vibe_reports"