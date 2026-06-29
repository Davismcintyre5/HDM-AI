from fastapi import APIRouter, HTTPException
from schemas.erp.query import QueryRequest
from schemas.erp.file import FileExtractRequest
from schemas.erp.alert import AlertAnalyzeRequest
from services.erp.query_service import erp_query_service
from services.erp.file_service import erp_file_service
from services.erp.alert_service import erp_alert_service

router = APIRouter(prefix="/erp", tags=["ERP AI"])

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

@router.post("/public/chat")
async def public_chat(request: QueryRequest):
    result = await erp_query_service.process_query(
        tenant_id="public",
        query=request.query,
        provider=request.provider or "groq",
        context={"source": "landing", **(request.context or {})},
        data=request.data,
    )
    return {"success": True, "data": result}

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

@router.post("/alert/analyze")
async def alert_analyze(request: AlertAnalyzeRequest):
    result = await erp_alert_service.analyze(
        tenant_id=request.tenant_id,
        data=request.data,
    )
    return {"success": True, "data": result}

@router.get("/health")
async def health():
    return {"success": True, "data": {"status": "healthy", "service": "erp_gateway"}}