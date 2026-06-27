# ====================================================================================================
# 5. server/schemas/vibe/creation.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class CreateHashtagsRequest(BaseModel):
    content: str
    count: int = 10
    data: Optional[dict] = None

class CreateCaptionRequest(BaseModel):
    image_description: str
    tone: Optional[str] = "engaging"
    platform: Optional[str] = "instagram"
    data: Optional[dict] = None

class CreateDescriptionRequest(BaseModel):
    title: str
    content_type: str
    length: Optional[str] = "medium"
    data: Optional[dict] = None

class CreateThumbnailRequest(BaseModel):
    title: str
    style: Optional[str] = "modern"
    data: Optional[dict] = None