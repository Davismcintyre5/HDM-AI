"""
HDM AI - General AI Code Execution Model
"""

from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional


class CodeExecution(Document):
    """Code execution record via Judge0."""
    user_id: Indexed(str)
    language: str
    code: str
    stdin: str = ""
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None
    execution_time_ms: Optional[float] = None
    status: str = "pending"  # pending, processing, completed, error
    judge0_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "code_executions"