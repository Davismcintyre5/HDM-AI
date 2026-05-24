# ====================================================================================================
# server/models/vault/security_scan.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class SecurityScan(Document):
    user_id: Indexed(str)
    scan_type: str  # password_audit, breach_check, device_scan, network_scan
    score: int = 0  # 0-100
    findings: list = []
    recommendations: list = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "vault_scans"