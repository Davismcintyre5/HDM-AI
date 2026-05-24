"""
HDM AI - General AI Learning Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class LearnRequest(BaseModel):
    topic: str = Field(default="General", min_length=1, max_length=200)
    subject: str = Field(default="general")
    level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class LearnResponse(BaseModel):
    reply: str
    session_id: str
    resources: dict = {}
    progress: float = 0.0


class QuizRequest(BaseModel):
    num_questions: int = Field(default=5, ge=1, le=20)


class QuizAnswerRequest(BaseModel):
    question_index: int = Field(..., ge=0)
    answer_index: int = Field(..., ge=0)