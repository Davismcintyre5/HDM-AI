# ====================================================================================================
# 3. server/schemas/vibe/moderation.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class ModTextRequest(BaseModel):
    text: str
    data: Optional[dict] = None

class ModImageRequest(BaseModel):
    image_url: str
    description: Optional[str] = None
    data: Optional[dict] = None

class ModVideoRequest(BaseModel):
    video_url: str
    description: Optional[str] = None
    data: Optional[dict] = None

class ModCommentRequest(BaseModel):
    comment: str
    data: Optional[dict] = None

class ModBatchRequest(BaseModel):
    items: list
    data: Optional[dict] = None