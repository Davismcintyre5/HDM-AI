# ====================================================================================================
# 33. server/services/general/learn_service.py
# ====================================================================================================
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from models.general.learn_session import LearnSession, QuizQuestion
from services.ai_service import ai_service
import json

class LearnService:
    async def learn(self, user_id: str, topic: str, subject: str, level: str, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        session = None
        if session_id: session = await LearnSession.get(session_id)
        if not session:
            session = LearnSession(user_id=user_id, topic=topic, subject=subject, level=level)
            await session.insert(); session_id = str(session.id)

        prompt = f"""You are an expert tutor teaching '{topic}' ({subject}) at {level} level.
User question: {message}
Provide a clear, educational response with examples and a key takeaway. Keep it appropriate for {level} level."""
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.5, max_tokens=2048, service="general")
        reply = result.get("reply", "")

        session.progress = min(100, session.progress + 5); session.updated_at = datetime.utcnow()
        await session.save()
        return {"reply": reply, "session_id": session_id, "resources": {"summary": reply[:500] + "..." if len(reply) > 500 else reply}, "progress": session.progress}

    async def get_quiz(self, session_id: str, num_questions: int = 5) -> Dict[str, Any]:
        session = await LearnSession.get(session_id)
        if not session: return {"success": False, "error": "Session not found"}
        prompt = f"""Generate {num_questions} multiple-choice quiz questions about '{session.topic}' at {session.level} level.
Return as JSON array: [{{"question": "...", "options": ["A", "B", "C", "D"], "correct_index": 0}}]"""
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.7, max_tokens=2048, service="general")
        try:
            questions = json.loads(result.get("reply", "[]"))
            session.quiz = [QuizQuestion(**q) for q in questions]
            session.total_questions = len(questions); await session.save()
            return {"session_id": session_id, "questions": [{"question": q.question, "options": q.options} for q in session.quiz]}
        except: return {"success": False, "error": "Could not generate quiz"}

    async def submit_answer(self, session_id: str, question_index: int, answer_index: int) -> Dict[str, Any]:
        session = await LearnSession.get(session_id)
        if not session or question_index >= len(session.quiz): return {"success": False, "error": "Invalid question"}
        question = session.quiz[question_index]; question.user_answer = answer_index; question.is_correct = (answer_index == question.correct_index)
        if question.is_correct: session.correct_answers += 1
        session.score = (session.correct_answers / session.total_questions) * 100 if session.total_questions > 0 else 0
        await session.save()
        return {"is_correct": question.is_correct, "correct_answer": question.correct_index, "score": session.score, "progress": session.progress}

    async def get_flashcards(self, session_id: str) -> Dict[str, Any]:
        session = await LearnSession.get(session_id)
        if not session: return {"success": False, "error": "Session not found"}
        if session.flashcards: return {"session_id": session_id, "flashcards": session.flashcards}
        prompt = f"Generate 10 flashcards about '{session.topic}' at {session.level} level. Return as JSON: [{{\"term\": \"...\", \"definition\": \"...\"}}]"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.5, max_tokens=2048, service="general")
        try:
            flashcards = json.loads(result.get("reply", "[]"))
            session.flashcards = flashcards; await session.save()
            return {"session_id": session_id, "flashcards": flashcards}
        except: return {"success": False, "error": "Could not generate flashcards"}

learn_service = LearnService()