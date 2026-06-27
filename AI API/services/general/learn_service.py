# ====================================================================================================
# HDM AI Engine - services/general/learn_service.py
# Stateless — MERN passes session state, Python does AI only
# ====================================================================================================

from typing import Dict, Any, Optional, List
from loguru import logger
from services.ai_service import ai_service
import json


class LearnService:

    async def learn(
        self,
        user_id: str,
        topic: str,
        subject: str,
        level: str,
        message: str,
        session_id: Optional[str] = None,
        session_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a learning response. MERN provides session context."""

        progress = session_data.get("progress", 0) if session_data else 0

        prompt = f"""You are an expert tutor teaching '{topic}' ({subject}) at {level} level.
User question: {message}
Provide a clear, educational response with examples and a key takeaway. Keep it appropriate for {level} level."""

        result = await ai_service.groq_chat(
            [{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2048,
            module="general",
        )
        reply = result.get("reply", "")

        return {
            "reply": reply,
            "session_id": session_id or "new",
            "resources": {"summary": reply[:500] + "..." if len(reply) > 500 else reply},
            "progress": min(100, progress + 5),
        }

    async def get_quiz(
        self,
        session_id: str,
        topic: str = "General",
        level: str = "beginner",
        num_questions: int = 5,
    ) -> Dict[str, Any]:
        """Generate quiz questions. MERN provides topic/level from its DB."""

        prompt = f"""Generate {num_questions} multiple-choice quiz questions about '{topic}' at {level} level.
Return as JSON array: [{{"question": "...", "options": ["A", "B", "C", "D"], "correct_index": 0}}]
Output ONLY the JSON array, no markdown, no explanation."""

        result = await ai_service.groq_chat(
            [{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
            module="general",
        )
        try:
            text = result.get("reply", "[]").replace("```json", "").replace("```", "").strip()
            questions = json.loads(text)
            return {
                "session_id": session_id,
                "questions": [
                    {"question": q["question"], "options": q["options"]}
                    for q in questions
                ],
            }
        except Exception as e:
            logger.error(f"Quiz parse error: {e}")
            return {"success": False, "error": "Could not generate quiz"}

    async def submit_answer(
        self,
        session_id: str,
        question_index: int,
        answer_index: int,
        quiz_data: List[Dict[str, Any]],
        session_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Check answer. MERN provides quiz data and session state."""

        if question_index >= len(quiz_data):
            return {"success": False, "error": "Invalid question"}

        question = quiz_data[question_index]
        correct_index = question.get("correct_index", 0)
        is_correct = (answer_index == correct_index)

        total = len(quiz_data)
        prev_correct = session_data.get("correct_answers", 0) if session_data else 0
        new_correct = prev_correct + (1 if is_correct else 0)
        score = (new_correct / total) * 100 if total > 0 else 0

        return {
            "is_correct": is_correct,
            "correct_answer": correct_index,
            "score": score,
            "progress": session_data.get("progress", 0) if session_data else 0,
        }

    async def get_flashcards(
        self,
        session_id: str,
        topic: str = "General",
        level: str = "beginner",
    ) -> Dict[str, Any]:
        """Generate flashcards. MERN provides topic/level."""

        prompt = f"""Generate 10 flashcards about '{topic}' at {level} level.
Return as JSON: [{{"term": "...", "definition": "..."}}]
Output ONLY the JSON array, no markdown, no explanation."""

        result = await ai_service.groq_chat(
            [{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2048,
            module="general",
        )
        try:
            text = result.get("reply", "[]").replace("```json", "").replace("```", "").strip()
            flashcards = json.loads(text)
            return {"session_id": session_id, "flashcards": flashcards}
        except Exception as e:
            logger.error(f"Flashcards parse error: {e}")
            return {"success": False, "error": "Could not generate flashcards"}


learn_service = LearnService()