# ====================================================================================================
# server/routes/general.py — COMPLETE
# ====================================================================================================
"""
HDM AI - General AI Routes
Chat, Learn, Code, Image, Analyze — with streaming, file upload, search, deep think, multi-provider
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional, List
from loguru import logger
import json
from datetime import datetime

from schemas.core import SuccessResponse
from schemas.general.learn import LearnRequest, QuizAnswerRequest
from schemas.general.execute import CodeExecuteRequest
from schemas.general.image import ImageGenerateRequest, ImageAnalyzeRequest
from schemas.general.analyze import AnalyzeRequest

from middleware.auth import get_current_user
from services.general.chat_service import chat_service
from services.general.learn_service import learn_service
from services.general.execute_service import execute_service
from services.general.image_service import image_service
from services.general.analyze_service import analyze_service
from services.ai_service import ai_service

from models.general.conversation import Conversation, Message, MessageRole
from routes.admin import _ai_config

router = APIRouter(prefix="/general", tags=["General AI"])


# ================================================================================================
# CHAT — Normal
# ================================================================================================

@router.post("/chat")
async def chat(
    message: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    interface: str = Form("client"),
    feature: str = Form("chat"),
    search_enabled: bool = Form(False),
    deep_think: bool = Form(False),
    files: List[UploadFile] = File(None),
    user: dict = Depends(get_current_user),
):
    """Multi-turn AI chat. Uses admin-configured provider (default: Groq)."""
    result = await chat_service.chat(
        user_id=user.get("sub"),
        message=message,
        conversation_id=conversation_id,
        interface=interface,
        feature=feature,
        search_enabled=search_enabled,
        deep_think=deep_think,
        files=files,
        provider=_ai_config.get("default_provider", "groq"),
        temperature=_ai_config.get("temperature", 0.7),
        max_tokens=_ai_config.get("max_tokens", 1024),
    )
    return SuccessResponse(data=result)


# ================================================================================================
# CHAT — Streaming
# ================================================================================================

@router.post("/chat/stream")
async def chat_stream(
    message: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    interface: str = Form("client"),
    search_enabled: bool = Form(False),
    deep_think: bool = Form(False),
    user: dict = Depends(get_current_user),
):
    """Streaming AI chat — response types out word by word."""

    async def generate():
        full_response = ""
        conv_id = conversation_id

        try:
            conversation = None
            if conv_id:
                conversation = await Conversation.get(conv_id)
            if not conversation:
                conversation = Conversation(
                    user_id=user.get("sub"),
                    title=message[:50] + ("..." if len(message) > 50 else ""),
                    interface=interface,
                )
                await conversation.insert()
                conv_id = str(conversation.id)

            await Message(
                conversation_id=conv_id,
                role=MessageRole.USER,
                content=message,
            ).insert()

            history = await Message.find(
                Message.conversation_id == conv_id
            ).sort(-Message.timestamp).limit(20).to_list()
            history.reverse()
            messages_list = [{"role": m.role.value, "content": m.content} for m in history]

            system_prompt = "You are HDM AI, a helpful assistant. Be concise, accurate, and friendly."
            if deep_think:
                system_prompt += " Use chain-of-thought reasoning. Think step by step."
            messages_list.insert(0, {"role": "system", "content": system_prompt})

            temperature = 0.2 if deep_think else _ai_config.get("temperature", 0.7)
            max_tokens_val = 4096 if deep_think else _ai_config.get("max_tokens", 1024)

            provider = _ai_config.get("default_provider", "groq")

            if provider == "gemini":
                prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages_list])
                result = await ai_service.gemini_chat(prompt, temperature=temperature, max_tokens=max_tokens_val)
                full_response = result.get("reply", "")
                yield f"data: {json.dumps({'chunk': full_response, 'conversation_id': conv_id})}\n\n"
                yield f"data: {json.dumps({'done': True, 'conversation_id': conv_id})}\n\n"
            else:
                async for chunk in ai_service.groq_chat_stream(
                    messages_list,
                    temperature=temperature,
                    max_tokens=max_tokens_val,
                    service="general",
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk, 'conversation_id': conv_id})}\n\n"
                yield f"data: {json.dumps({'done': True, 'conversation_id': conv_id})}\n\n"

            await Message(
                conversation_id=conv_id,
                role=MessageRole.ASSISTANT,
                content=full_response,
            ).insert()

            conversation.message_count += 2
            conversation.updated_at = datetime.utcnow()
            conversation.last_message = full_response[:100]
            await conversation.save()

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ================================================================================================
# CONVERSATIONS
# ================================================================================================

@router.get("/conversations")
async def list_conversations(user: dict = Depends(get_current_user)):
    conversations = await chat_service.get_conversations(user.get("sub"))
    return SuccessResponse(data=conversations)


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, user: dict = Depends(get_current_user)):
    messages = await chat_service.get_messages(conversation_id)
    return SuccessResponse(data=messages)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user: dict = Depends(get_current_user)):
    success = await chat_service.delete_conversation(conversation_id, user.get("sub"))
    if not success:
        raise HTTPException(404, "Conversation not found")
    return SuccessResponse(message="Conversation deleted")


# ================================================================================================
# LEARN
# ================================================================================================

@router.post("/learn")
async def learn(request: LearnRequest, user: dict = Depends(get_current_user)):
    result = await learn_service.learn(
        user_id=user.get("sub"), topic=request.topic, subject=request.subject,
        level=request.level, message=request.message, session_id=request.session_id,
    )
    return SuccessResponse(data=result)


@router.get("/learn/{session_id}/quiz")
async def get_quiz(session_id: str, user: dict = Depends(get_current_user)):
    result = await learn_service.get_quiz(session_id)
    return SuccessResponse(data=result)


@router.post("/learn/{session_id}/quiz")
async def submit_quiz(session_id: str, request: QuizAnswerRequest, user: dict = Depends(get_current_user)):
    result = await learn_service.submit_answer(session_id, request.question_index, request.answer_index)
    return SuccessResponse(data=result)


@router.get("/learn/{session_id}/flashcards")
async def get_flashcards(session_id: str, user: dict = Depends(get_current_user)):
    result = await learn_service.get_flashcards(session_id)
    return SuccessResponse(data=result)


# ================================================================================================
# CODE EXECUTION
# ================================================================================================

@router.post("/execute")
async def execute(request: CodeExecuteRequest, user: dict = Depends(get_current_user)):
    result = await execute_service.execute(user.get("sub"), request.language, request.code, request.stdin)
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Execution failed"))
    return SuccessResponse(data=result)


@router.get("/execute/languages")
async def get_languages():
    result = await execute_service.get_supported_languages()
    return SuccessResponse(data=result)


@router.get("/execute/{execution_id}")
async def get_execution(execution_id: str, user: dict = Depends(get_current_user)):
    result = await execute_service.get_execution(execution_id, user.get("sub"))
    if not result: raise HTTPException(404, "Not found")
    return SuccessResponse(data=result)


# ================================================================================================
# IMAGE
# ================================================================================================

@router.post("/image")
async def generate_image(request: ImageGenerateRequest, user: dict = Depends(get_current_user)):
    result = await image_service.generate(user.get("sub"), request.prompt, request.style, request.size, request.num_images)
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Generation failed"))
    return SuccessResponse(data=result)


@router.post("/image/analyze")
async def analyze_image(request: ImageAnalyzeRequest, user: dict = Depends(get_current_user)):
    result = await image_service.analyze_image(request.image_base64, request.prompt)
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Analysis failed"))
    return SuccessResponse(data=result)


@router.post("/image/variations")
async def generate_variations(request: ImageAnalyzeRequest, user: dict = Depends(get_current_user)):
    result = await image_service.generate_variations(request.image_base64)
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Failed"))
    return SuccessResponse(data=result)


# ================================================================================================
# ANALYZE
# ================================================================================================

@router.post("/analyze")
async def analyze(request: AnalyzeRequest, user: dict = Depends(get_current_user)):
    result = await analyze_service.analyze(request.content, request.analysis_type)
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Analysis failed"))
    return SuccessResponse(data=result)