# ====================================================================================================
# HDM AI Engine - routes/erp.py
# ERP AI Gateway — Stateless, No Auth, No DB
# ====================================================================================================

from fastapi import APIRouter, HTTPException
from schemas.erp.query import QueryRequest
from schemas.erp.file import FileExtractRequest
from schemas.erp.alert import AlertAnalyzeRequest
from services.erp.query_service import erp_query_service
from services.erp.file_service import erp_file_service
from services.erp.alert_service import erp_alert_service

router = APIRouter(prefix="/erp", tags=["ERP AI"])


# ================================================================================================
# QUERY — AI-powered business queries with real data
# ================================================================================================

@router.post("/query")
async def query(request: QueryRequest):
    result = await erp_query_service.process_query(
        tenant_id=request.tenant_id,
        query=request.query,
        provider=request.provider or "groq",
        context=request.context,
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# FILE EXTRACTION
# ================================================================================================

@router.post("/file/extract")
async def file_extract(request: FileExtractRequest):
    result = await erp_file_service.extract_text(
        tenant_id=request.tenant_id,
        filename=request.filename,
        file_type=request.file_type,
        content=request.content,
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# PROACTIVE ALERTS
# ================================================================================================

@router.post("/alert/analyze")
async def alert_analyze(request: AlertAnalyzeRequest):
    result = await erp_alert_service.analyze(
        tenant_id=request.tenant_id,
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# HEALTH CHECK
# ================================================================================================

@router.get("/health")
async def health():
    return {"success": True, "data": {"status": "healthy", "service": "erp_gateway"}}