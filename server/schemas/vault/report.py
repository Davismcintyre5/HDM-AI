# ====================================================================================================
# 4. server/schemas/vault/report.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class ReportGenerateRequest(BaseModel):
    user_id: str
    report_type: str = "security_overview"  # security_overview, password_report, breach_report
    data: Optional[dict] = None  # real security metrics

class ReportScheduleRequest(BaseModel):
    user_id: str
    report_type: str
    webhook_url: str
    frequency: str = "weekly"  # daily, weekly, monthly
    data: Optional[dict] = None  # email, preferences