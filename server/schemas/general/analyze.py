"""
HDM AI - General AI Content Analysis Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Any


class AnalyzeRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)
    analysis_type: str = Field(default="summary", pattern="^(summary|sentiment|keywords|entities|data|full)$")


class AnalyzeResponse(BaseModel):
    result: Any
    analysis_type: str
    confidence: float = 0.0