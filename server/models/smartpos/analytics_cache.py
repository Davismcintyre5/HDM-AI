# ====================================================================================================
# server/models/smartpos/analytics_cache.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional, Dict, Any

class AnalyticsCache(Document):
    business_id: Indexed(str)
    cache_type: str  # sales, products, customers, employees
    data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    class Settings: name = "smartpos_analytics_cache"