# server/schemas/vault/report.py
from pydantic import BaseModel, Field
from typing import Optional

class ReportGenerateRequest(BaseModel):
    user_id: str
    report_type: str = "security_overview"
    data: Optional[dict] = None

class ReportScheduleRequest(BaseModel):
    user_id: str
    report_type: str
    webhook_url: str
    frequency: str = "weekly"
    data: Optional[dict] = None

class ReportResponse(BaseModel):
    report_id: str
    content: str = ""
    format: str = "text"