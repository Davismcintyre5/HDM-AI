"""
HDM AI - General AI Learning Session Models
"""

from beanie import Document, Indexed
from pydantic import Field, BaseModel
from datetime import datetime
from typing import Optional, List


class QuizQuestion(BaseModel):
    """Embedded quiz question."""
    question: str
    options: List[str]
    correct_index: int
    user_answer: Optional[int] = None
    is_correct: Optional[bool] = None


class LearnSession(Document):
    """Learning session with quiz and flashcard support."""
    user_id: Indexed(str)
    topic: str
    subject: str = "general"
    level: str = "beginner"  # beginner, intermediate, advanced
    summary: Optional[str] = None
    flashcards: List[dict] = []  # [{term: "", definition: ""}]
    quiz: List[QuizQuestion] = []
    score: Optional[float] = None
    progress: float = 0.0
    total_questions: int = 0
    correct_answers: int = 0
    is_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "learn_sessions"