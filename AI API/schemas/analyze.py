from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    user_id: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=50000)
    analysis_type: str = Field(
        default="summary",
        pattern="^(summary|sentiment|keywords|entities|data|full)$"
    )