# ====================================================================================================
# server/schemas/vibe/moderation.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class ModTextRequest(BaseModel):
    text: str

class ModImageRequest(BaseModel):
    image_url: str
    description: Optional[str] = None

class ModVideoRequest(BaseModel):
    video_url: str
    description: Optional[str] = None

class ModCommentRequest(BaseModel):
    comment: str

class ModBatchRequest(BaseModel):
    items: list