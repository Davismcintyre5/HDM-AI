# ====================================================================================================
# HDM AI Engine — /v1/analyze
# ====================================================================================================

from fastapi import APIRouter
from schemas.analyze import AnalyzeRequest
from services.analyze_service import analyze_service

router = APIRouter(prefix="/v1", tags=["Analyze"])


@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    result = await analyze_service.analyze(
        user_id=request.user_id or "anon",
        content=request.content,
        analysis_type=request.analysis_type,
    )
    return {"success": True, "data": result}