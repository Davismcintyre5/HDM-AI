from fastapi import APIRouter
from services.ai_service import ai_service

router = APIRouter(prefix="/learn", tags=["Learning Studio"])

@router.post("/chat")
async def chat(req: dict):
    message = req.get("message", "")
    messages = req.get("messages", [])
    provider = req.get("provider", "groq")
    user_id = req.get("user_id", "learn")

    if messages:
        result = await ai_service.groq_chat(messages, max_tokens=1500, module="learn")
    else:
        system_prompt = req.get("system_prompt", "You are HDM AI Learning Assistant. Teach and guide the student.")
        result = await ai_service.groq_chat(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}],
            max_tokens=1500, module="learn"
        )
    return {
        "reply": result.get("reply", ""),
        "tokens_used": result.get("tokens_used", 0),
        "model": result.get("model", ""),
    }

@router.get("/health")
async def health():
    return {"status": "healthy", "service": "learn"}