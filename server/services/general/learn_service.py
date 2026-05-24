"""
HDM AI - General AI Learning Service
Topics, quizzes, and flashcards
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from models.general.learn_session import LearnSession, QuizQuestion
from services.ai_service import ai_service


class LearnService:
    """Learning session service."""

    async def learn(
        self,
        user_id: str,
        topic: str,
        subject: str,
        level: str,
        message: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a learning interaction."""

        # Get or create session
        session = None
        if session_id:
            session = await LearnSession.get(session_id)

        if not session:
            session = LearnSession(
                user_id=user_id,
                topic=topic,
                subject=subject,
                level=level,
            )
            await session.insert()
            session_id = str(session.id)

        # Build prompt based on context
        prompt = self._build_learn_prompt(session, message)
        result = await ai_service.groq_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2048,
        )
        reply = result.get("reply", "")

        # Parse and extract learning content
        resources = await self._extract_resources(topic, reply)

        # Update session
        session.progress = min(100, session.progress + 5)
        session.updated_at = datetime.utcnow()
        await session.save()

        logger.info(f"Learn: user={user_id}, topic={topic}, progress={session.progress}%")

        return {
            "reply": reply,
            "session_id": session_id,
            "resources": resources,
            "progress": session.progress,
        }

    async def get_quiz(
        self,
        session_id: str,
        num_questions: int = 5,
    ) -> Dict[str, Any]:
        """Generate quiz questions for a session."""
        session = await LearnSession.get(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        prompt = f"""Generate {num_questions} multiple-choice quiz questions about '{session.topic}' at {session.level} level.
Return as JSON array: [{{"question": "...", "options": ["A", "B", "C", "D"], "correct_index": 0}}]"""

        result = await ai_service.groq_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )

        questions = self._parse_quiz_json(result.get("reply", "[]"))
        session.quiz = [QuizQuestion(**q) for q in questions]
        session.total_questions = len(questions)
        await session.save()

        return {
            "session_id": session_id,
            "questions": [{"question": q.question, "options": q.options} for q in session.quiz],
        }

    async def submit_answer(
        self,
        session_id: str,
        question_index: int,
        answer_index: int,
    ) -> Dict[str, Any]:
        """Submit a quiz answer."""
        session = await LearnSession.get(session_id)
        if not session or question_index >= len(session.quiz):
            return {"success": False, "error": "Invalid question"}

        question = session.quiz[question_index]
        question.user_answer = answer_index
        question.is_correct = (answer_index == question.correct_index)

        if question.is_correct:
            session.correct_answers += 1

        session.score = (session.correct_answers / session.total_questions) * 100 if session.total_questions > 0 else 0
        await session.save()

        return {
            "is_correct": question.is_correct,
            "correct_answer": question.correct_index,
            "score": session.score,
            "progress": session.progress,
        }

    async def get_flashcards(self, session_id: str) -> Dict[str, Any]:
        """Generate flashcards for a session."""
        session = await LearnSession.get(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        if session.flashcards:
            return {"session_id": session_id, "flashcards": session.flashcards}

        prompt = f"""Generate 10 flashcards about '{session.topic}' at {session.level} level.
Return as JSON: [{{"term": "...", "definition": "..."}}]"""

        result = await ai_service.groq_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2048,
        )

        import json
        try:
            flashcards = json.loads(result.get("reply", "[]"))
            session.flashcards = flashcards
            await session.save()
        except json.JSONDecodeError:
            flashcards = []

        return {"session_id": session_id, "flashcards": flashcards}

    def _build_learn_prompt(self, session: LearnSession, message: str) -> str:
        """Build learning prompt with context."""
        return f"""You are an expert tutor teaching '{session.topic}' ({session.subject}) at {session.level} level.

User question: {message}

Provide a clear, educational response. Include:
1. Direct answer to the question
2. Simple examples if applicable
3. A key takeaway

Keep it appropriate for {session.level} level."""

    async def _extract_resources(self, topic: str, reply: str) -> Dict[str, Any]:
        """Extract learning resources from reply."""
        return {
            "summary": reply[:500] + "..." if len(reply) > 500 else reply,
            "key_points": self._extract_key_points(reply),
        }

    def _extract_key_points(self, text: str) -> list:
        """Extract key bullet points from text."""
        points = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith(("- ", "* ", "• ", "1.", "2.", "3.")):
                points.append(line.lstrip("- *• 1234567890.").strip())
        return points[:5] if points else []

    def _parse_quiz_json(self, text: str) -> list:
        """Parse quiz JSON from AI response."""
        import json
        import re

        try:
            # Try direct JSON parse
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON array
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
        return []


learn_service = LearnService()