from fastapi import APIRouter
from services.rvnp.moderation_service import moderation_service
from services.rvnp.verification_service import verification_service
from services.rvnp.feed_ranking_service import feed_ranking_service
from services.rvnp.suggestions_service import suggestions_service
from services.rvnp.trending_service import trending_service
from services.ai_service import ai_service

router = APIRouter(prefix="/rvnp", tags=["RVNP Campus Hub"])

@router.post("/chat")
async def chat(req: dict):
    message = req.get("message", "")
    system_prompt = req.get("system_prompt", "You are HDM AI, the assistant for RVNP Campus Hub. Answer questions helpfully and accurately.")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]
    result = await ai_service.groq_chat(messages, max_tokens=800, module="rvnp")
    return {"reply": result.get("reply", ""), "tokens_used": result.get("tokens_used", 0), "model": result.get("model", "")}

@router.post("/moderate")
async def moderate(req: dict):
    result = await moderation_service.moderate(text=req.get("text"), imageUrl=req.get("imageUrl"))
    return result

@router.post("/verify-document")
async def verify_document(req: dict):
    result = await verification_service.scan_document(imageUrl=req.get("imageUrl"))
    return result

@router.post("/rank-feed")
async def rank_feed(req: dict):
    result = await feed_ranking_service.rank(
        posts=req.get("posts", []),
        userInterests=req.get("userInterests"),
        userDepartment=req.get("userDepartment"),
        userHostel=req.get("userHostel"),
    )
    return result

@router.post("/suggest-replies")
async def suggest_replies(req: dict):
    chatContext = req.get("chatContext", {})
    result = await suggestions_service.suggest(
        lastMessages=chatContext.get("lastMessages", []),
        chatType=chatContext.get("chatType", "direct"),
        relationship=chatContext.get("relationship", "classmate"),
    )
    return result

@router.post("/trending")
async def trending(req: dict):
    result = await trending_service.detect(posts=req.get("posts", []))
    return result

@router.get("/health")
async def health():
    return {"status": "healthy", "service": "rvnp_campus_hub"}