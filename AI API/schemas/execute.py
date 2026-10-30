from pydantic import BaseModel, Field
from typing import Optional


class ExecuteRequest(BaseModel):
    user_id: Optional[str] = None
    language: str = Field(default="python")
    code: str = Field(..., min_length=1, max_length=50000)
    stdin: str = Field(default="", max_length=10000)