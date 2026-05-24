# ====================================================================================================
# server/schemas/vault/report.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class ReportGenerateRequest(BaseModel):
    user_id: str
    report_type: str = "security_overview"  # security_overview, password_report, breach_report

class ReportScheduleRequest(BaseModel):
    user_id: str
    report_type: str
    webhook_url: str
    frequency: str = "weekly"  # daily, weekly, monthly

class ReportResponse(BaseModel):
    report_id: str
    content: str = ""
    format: str = "text"