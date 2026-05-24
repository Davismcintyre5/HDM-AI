# ====================================================================================================
# server/models/vault/report.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class VaultReport(Document):
    user_id: Indexed(str)
    report_type: str  # security_overview, password_report, breach_report
    content: str
    format: str = "text"  # text, pdf
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "vault_reports"