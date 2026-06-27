from pydantic import BaseModel, Field
from typing import Optional, List

class ImageGenerateRequest(BaseModel):
    user_id: Optional[str] = None
    prompt: str = Field(..., min_length=1, max_length=1000)
    style: str = Field(default="realistic")
    size: str = Field(default="1024x1024")
    num_images: int = Field(default=1, ge=1, le=4)

class ImageResponse(BaseModel):
    images: List[dict]
    revised_prompt: str
    style: str
    count: int

class ImageAnalyzeRequest(BaseModel):
    user_id: Optional[str] = None
    image_base64: str = Field(..., min_length=1)
    prompt: str = Field(default="Describe this image in detail.")