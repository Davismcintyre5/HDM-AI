from pydantic import BaseModel, Field
from typing import Optional


class ImageRequest(BaseModel):
    user_id: Optional[str] = None
    prompt: str = Field(..., min_length=1, max_length=1000)
    style: str = Field(default="realistic")
    size: str = Field(default="1024x1024")
    num_images: int = Field(default=1, ge=1, le=4)
    mode: str = Field(default="generate", pattern="^(generate|analyze|variations)$")
    image_base64: Optional[str] = None