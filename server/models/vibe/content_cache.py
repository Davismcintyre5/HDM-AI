# ====================================================================================================
# server/models/vibe/content_cache.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional, Dict, Any

class ContentCache(Document):
    content_id: Indexed(str)
    content_type: str
    data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    class Settings: name = "vibe_content_cache"