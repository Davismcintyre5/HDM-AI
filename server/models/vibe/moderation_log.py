# ====================================================================================================
# server/models/vibe/moderation_log.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class ModerationLog(Document):
    content_id: Indexed(str)
    content_type: str  # text, image, video, comment
    flagged: bool = False
    category: str = ""  # spam, hate_speech, nsfw, graphic, harassment
    confidence: float = 0.0
    action: str = "flagged"  # flagged, allowed, removed
    moderator: str = "ai"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "vibe_moderation_logs"