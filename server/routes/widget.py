# ====================================================================================================
# server/routes/widget.py (FULL - 2 endpoints)
# ====================================================================================================
from fastapi import APIRouter, Depends
from middleware.auth import get_project_auth
from schemas.widget.chat import ChatRequest
from services.widget.chat_service import widget_chat_service
from services.widget.context_service import widget_context_service

router = APIRouter(prefix="/widget", tags=["Widget AI"])
A = Depends(get_project_auth("widget"))

@router.post("/chat")
async def chat(request: ChatRequest, auth=Depends(get_project_auth("widget"))):
    # Merge request context with default context
    context = await widget_context_service.get_context(request.source)
    if request.context:
        context.update(request.context)

    result = await widget_chat_service.chat(
        source=request.source,
        message=request.message,
        conversation_id=request.conversation_id,
        user_id=request.user_id,
        context=context,
    )
    return {"success": True, "data": result}

@router.get("/health")
async def health():
    return {"success": True, "data": {"status": "healthy", "source": "widget_ai"}}