# ====================================================================================================
# HDM AI Engine — /v1/chat
# ====================================================================================================

from fastapi import APIRouter
from schemas.chat import ChatRequest
from services.chat_service import chat_service

router = APIRouter(prefix="/v1", tags=["Chat"])


@router.post("/chat")
async def chat(request: ChatRequest):
    result = await chat_service.chat(
        user_id=request.user_id or "anon",
        message=request.message,
        messages=request.messages,
        provider=request.provider or "groq",
        model=request.model,
        temperature=request.temperature or 0.7,
        max_tokens=request.max_tokens or 4096,
        system_prompt=request.system_prompt,
        data=request.data,
        search_enabled=request.search_enabled or False,
        deep_think=request.deep_think or False,
    )
    return {"success": True, "data": result}