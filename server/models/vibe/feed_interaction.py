# ====================================================================================================
# server/models/vibe/feed_interaction.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class FeedInteraction(Document):
    user_id: Indexed(str)
    content_id: str
    interaction_type: str  # view, like, comment, share, save
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "vibe_feed_interactions"