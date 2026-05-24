# ====================================================================================================
# server/schemas/smartpos/report.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class ReportRequest(BaseModel):
    business_id: str
    report_type: str  # sales, inventory, tax, summary
    period: Optional[str] = "this_month"

class ReportResponse(BaseModel):
    report_text: str = ""
    format: str = "text"