# ====================================================================================================
# server/schemas/vibe/accessibility.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class AltTextRequest(BaseModel):
    image_url: str
    description: Optional[str] = None

class CaptionsRequest(BaseModel):
    video_url: str
    language: str = "en"

class TextToSpeechRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"
    language: str = "en"