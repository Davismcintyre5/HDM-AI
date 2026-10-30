# ====================================================================================================
# HDM AI Engine — /v1/execute
# ====================================================================================================

from fastapi import APIRouter
from schemas.execute import ExecuteRequest
from services.execute_service import execute_service

router = APIRouter(prefix="/v1", tags=["Execute"])


@router.post("/execute")
async def execute(request: ExecuteRequest):
    result = await execute_service.execute(
        user_id=request.user_id or "anon",
        language=request.language,
        code=request.code,
        stdin=request.stdin,
    )
    return {"success": True, "data": result}


@router.get("/execute/languages")
async def languages():
    result = await execute_service.get_languages()
    return {"success": True, "data": result}