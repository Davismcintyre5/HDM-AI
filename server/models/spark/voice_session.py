# ====================================================================================================
# server/models/spark/voice_session.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class VoiceSession(Document):
    user_id: Indexed(str)
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    response_text: Optional[str] = None
    response_audio_url: Optional[str] = None
    language: str = "en"
    duration_seconds: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "spark_voice_sessions"