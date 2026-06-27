from fastapi import APIRouter
from schemas.widget.chat import ChatRequest
from services.widget.chat_service import widget_chat_service
from services.widget.context_service import widget_context_service

router = APIRouter(prefix="/widget", tags=["Widget AI"])

@router.post("/chat")
async def chat(request: ChatRequest):
    context = await widget_context_service.get_context(request.source)
    if request.context:
        context.update(request.context)

    result = await widget_chat_service.chat(
        source=request.source,
        message=request.message,
        messages=request.messages,
        user_id=request.user_id,
        context=context,
    )
    return {"success": True, "data": result}

@router.get("/health")
async def health():
    return {"success": True, "data": {"status": "healthy", "source": "widget_ai"}}