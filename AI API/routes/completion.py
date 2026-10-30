# ====================================================================================================
# HDM AI Engine — /v1/completion
# External systems — Key 3 → Key 4 auto-failover
# ====================================================================================================

from fastapi import APIRouter
from schemas.completion import CompletionRequest
from services.completion_service import completion_service

router = APIRouter(prefix="/v1", tags=["Completion"])


@router.post("/completion")
async def completion(request: CompletionRequest):
    result = await completion_service.complete(
        user_id=request.user_id or "external",
        message=request.message,
        messages=request.messages,
        system_prompt=request.system_prompt,
        temperature=request.temperature or 0.7,
        max_tokens=request.max_tokens or 4096,
        data=request.data,
    )
    return {"success": True, "data": result}