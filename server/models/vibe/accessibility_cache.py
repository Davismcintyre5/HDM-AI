# ====================================================================================================
# server/models/vibe/accessibility_cache.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class AccessibilityCache(Document):
    content_id: Indexed(str)
    alt_text: Optional[str] = None
    captions: Optional[str] = None
    audio_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "vibe_accessibility_cache"