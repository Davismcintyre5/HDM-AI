# ====================================================================================================
# server/schemas/vibe/search.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 20

class VisualSearchRequest(BaseModel):
    image_url: str
    limit: int = 10

class VoiceSearchRequest(BaseModel):
    audio_url: str
    language: str = "en"