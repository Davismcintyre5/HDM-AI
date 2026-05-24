# ====================================================================================================
# server/schemas/vibe/creation.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional, List

class CreateHashtagsRequest(BaseModel):
    content: str
    count: int = 10

class CreateCaptionRequest(BaseModel):
    image_description: str
    tone: Optional[str] = "engaging"
    platform: Optional[str] = "instagram"

class CreateDescriptionRequest(BaseModel):
    title: str
    content_type: str
    length: Optional[str] = "medium"

class CreateThumbnailRequest(BaseModel):
    title: str
    style: Optional[str] = "modern"