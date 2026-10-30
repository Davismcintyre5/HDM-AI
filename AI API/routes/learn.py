# ====================================================================================================
# HDM AI Engine — /v1/learn/chat
# ====================================================================================================

from fastapi import APIRouter
from schemas.learn import LearnChatRequest
from services.learn_service import learn_service

router = APIRouter(prefix="/v1/learn", tags=["Learn"])


@router.post("/chat")
async def chat(request: LearnChatRequest):
    result = await learn_service.chat(
        user_id=request.user_id or "anon",
        message=request.message,
        messages=request.messages,
        system_prompt=request.system_prompt,
        temperature=request.temperature or 0.5,
        max_tokens=request.max_tokens or 4096,
        data=request.data,
    )
    return {"success": True, "data": result}