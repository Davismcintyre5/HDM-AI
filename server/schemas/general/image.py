"""
HDM AI - General AI Image Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    style: str = Field(default="realistic", pattern="^(realistic|cartoon|anime|oil-painting|watercolor|sketch|3d-render|pixel-art)$")
    size: str = Field(default="1024x1024")
    num_images: int = Field(default=1, ge=1, le=4)


class ImageResponse(BaseModel):
    images: List[dict]
    revised_prompt: str
    style: str
    count: int


class ImageAnalyzeRequest(BaseModel):
    image_base64: str = Field(..., min_length=1)
    prompt: str = Field(default="Describe this image in detail.")