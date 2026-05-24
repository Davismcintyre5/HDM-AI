# ====================================================================================================
# server/models/spark/moderation_log.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class ModerationLog(Document):
    user_id: Indexed(str)
    content_type: str  # text, image, link
    flagged: bool = False
    category: str = ""  # spam, hate_speech, nsfw, child_safety, impersonation, self_harm
    confidence: float = 0.0
    action: str = "flagged"  # flagged, allowed, blocked
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "spark_moderation_logs"