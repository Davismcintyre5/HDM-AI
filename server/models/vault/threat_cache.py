# ====================================================================================================
# server/models/vault/threat_cache.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional, Dict, Any

class ThreatCache(Document):
    user_id: Indexed(str)
    threat_type: str
    data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    class Settings: name = "vault_threat_cache"