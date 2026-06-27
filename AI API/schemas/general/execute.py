"""
HDM AI - General AI Code Execution Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class CodeExecuteRequest(BaseModel):
    user_id: Optional[str] = None
    language: str = Field(default="python")
    code: str = Field(..., min_length=1, max_length=50000)
    stdin: str = Field(default="", max_length=10000)


class CodeExecuteResponse(BaseModel):
    execution_id: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None
    execution_time_ms: float = 0
    status: str


class LanguageResponse(BaseModel):
    languages: List[dict]