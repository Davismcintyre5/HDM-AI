# ====================================================================================================
# HDM AI Engine - routes/general.py
# General AI Routes — Stateless, No Auth, No DB Writes
# ====================================================================================================

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional, List
from loguru import logger
import json
from datetime import datetime

from schemas.general.chat import ChatRequest
from schemas.general.learn import LearnRequest, QuizRequest, QuizAnswerRequest, FlashcardsRequest
from schemas.general.execute import CodeExecuteRequest
from schemas.general.image import ImageGenerateRequest, ImageAnalyzeRequest
from schemas.general.analyze import AnalyzeRequest

from services.general.chat_service import chat_service
from services.general.learn_service import learn_service
from services.general.execute_service import execute_service
from services.general.image_service import image_service
from services.general.analyze_service import analyze_service
from services.ai_service import ai_service

router = APIRouter(prefix="/general", tags=["General AI"])


# ================================================================================================
# CHAT
# ================================================================================================

@router.post("/chat")
async def chat(request: ChatRequest):
    """AI chat — stateless. MERN sends full message history."""
    result = await chat_service.chat(
        user_id=request.user_id,
        message=request.message,
        messages=request.messages,
        provider=request.provider or "groq",
        model=request.model,
        temperature=request.temperature or 0.7,
        max_tokens=request.max_tokens or 1024,
        search_enabled=request.search_enabled or False,
        deep_think=request.deep_think or False,
        system_prompt=request.system_prompt,
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# CHAT STREAMING
# ================================================================================================

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming AI chat — tokens sent via SSE."""

    async def generate():
        full_response = ""
        try:
            messages_list = request.messages or []
            if not messages_list:
                messages_list = [{"role": "user", "content": request.message}]

            system_prompt = request.system_prompt or "You are HDM AI, a helpful assistant."
            if request.deep_think:
                system_prompt += " Use chain-of-thought reasoning."
            messages_list.insert(0, {"role": "system", "content": system_prompt})

            provider = request.provider or "groq"

            if provider == "gemini":
                prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages_list])
                result = await ai_service.gemini_chat(
                    prompt,
                    temperature=request.temperature or 0.7,
                    max_tokens=request.max_tokens or 1024,
                    module="general",
                )
                full_response = result.get("reply", "")
                yield f"data: {json.dumps({'chunk': full_response, 'done': True})}\n\n"
            else:
                async for chunk in ai_service.groq_chat_stream(
                    messages_list,
                    temperature=request.temperature or 0.7,
                    max_tokens=request.max_tokens or 1024,
                    module="general",
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


# ================================================================================================
# LEARN
# ================================================================================================

@router.post("/learn")
async def learn(request: LearnRequest):
    result = await learn_service.learn(
        user_id=request.user_id,
        topic=request.topic,
        subject=request.subject,
        level=request.level,
        message=request.message,
        session_id=request.session_id,
        session_data=request.session_data,
    )
    return {"success": True, "data": result}


@router.post("/learn/quiz")
async def get_quiz(request: QuizRequest):
    result = await learn_service.get_quiz(
        session_id=request.session_id,
        topic=request.topic,
        level=request.level,
        num_questions=request.num_questions,
    )
    return {"success": True, "data": result}


@router.post("/learn/quiz/submit")
async def submit_quiz(request: QuizAnswerRequest):
    result = await learn_service.submit_answer(
        session_id=request.session_id,
        question_index=request.question_index,
        answer_index=request.answer_index,
        quiz_data=request.quiz_data,
        session_data=request.session_data,
    )
    return {"success": True, "data": result}


@router.post("/learn/flashcards")
async def get_flashcards(request: FlashcardsRequest):
    result = await learn_service.get_flashcards(
        session_id=request.session_id,
        topic=request.topic,
        level=request.level,
    )
    return {"success": True, "data": result}


# ================================================================================================
# CODE EXECUTION
# ================================================================================================

@router.post("/execute")
async def execute(request: CodeExecuteRequest):
    result = await execute_service.execute(request.user_id, request.language, request.code, request.stdin)
    return {"success": True, "data": result}


@router.get("/execute/languages")
async def get_languages():
    return {"success": True, "data": await execute_service.get_supported_languages()}


@router.get("/execute/{execution_id}")
async def get_execution(execution_id: str):
    result = await execute_service.get_execution(execution_id, "system")
    if not result:
        return {"success": False, "error": "Not found"}
    return {"success": True, "data": result}


# ================================================================================================
# IMAGE
# ================================================================================================

@router.post("/image")
async def generate_image(request: ImageGenerateRequest):
    result = await image_service.generate(request.user_id, request.prompt, request.style, request.size, request.num_images)
    return {"success": True, "data": result}


@router.post("/image/analyze")
async def analyze_image(request: ImageAnalyzeRequest):
    result = await image_service.analyze_image(request.image_base64, request.prompt)
    return {"success": True, "data": result}


@router.post("/image/variations")
async def generate_variations(request: ImageAnalyzeRequest):
    result = await image_service.generate_variations(request.image_base64)
    return {"success": True, "data": result}


# ================================================================================================
# ANALYZE
# ================================================================================================

@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    result = await analyze_service.analyze(request.content, request.analysis_type)
    return {"success": True, "data": result}