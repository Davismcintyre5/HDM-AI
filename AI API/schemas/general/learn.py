from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LearnRequest(BaseModel):
    user_id: Optional[str] = None
    topic: str = Field(default="General", min_length=1, max_length=200)
    subject: str = Field(default="general")
    level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None

class LearnResponse(BaseModel):
    reply: str
    session_id: str
    resources: dict = {}
    progress: float = 0.0

class QuizRequest(BaseModel):
    session_id: str
    topic: str = "General"
    level: str = "beginner"
    num_questions: int = Field(default=5, ge=1, le=20)

class QuizAnswerRequest(BaseModel):
    session_id: str
    question_index: int = Field(..., ge=0)
    answer_index: int = Field(..., ge=0)
    quiz_data: List[Dict[str, Any]] = []
    session_data: Optional[Dict[str, Any]] = None

class FlashcardsRequest(BaseModel):
    session_id: str
    topic: str = "General"
    level: str = "beginner"