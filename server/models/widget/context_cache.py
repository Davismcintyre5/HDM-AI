# ====================================================================================================
# server/models/widget/context_cache.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional, Dict, Any

class ContextCache(Document):
    source: Indexed(str)  # "docusoft" or "hdm_portfolio"
    context_data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    class Settings: name = "widget_context_cache"