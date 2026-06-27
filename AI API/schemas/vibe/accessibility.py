# ====================================================================================================
# 9. server/schemas/vibe/accessibility.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class AltTextRequest(BaseModel):
    image_url: str
    description: Optional[str] = None
    data: Optional[dict] = None

class CaptionsRequest(BaseModel):
    video_url: str
    language: str = "en"
    data: Optional[dict] = None

class TextToSpeechRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"
    language: str = "en"
    data: Optional[dict] = None