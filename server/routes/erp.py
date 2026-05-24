# ====================================================================================================
# server/routes/erp.py (FULL)
# ====================================================================================================
"""
HDM AI - ERP AI Gateway Routes
Real data analysis for landing page, tenant queries, file extraction, alerts, stats
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from middleware.auth import get_project_auth
from schemas.erp.query import QueryRequest
from schemas.erp.file import FileExtractRequest
from schemas.erp.alert import AlertAnalyzeRequest
from services.erp.query_service import erp_query_service
from services.erp.file_service import erp_file_service
from services.erp.alert_service import erp_alert_service
from services.erp.stats_service import erp_stats_service

router = APIRouter(prefix="/erp", tags=["ERP AI"])
A = Depends(get_project_auth("erp"))


# ================================================================================================
# QUERY — AI-powered business queries with real data
# ================================================================================================

@router.post("/query")
async def query(request: QueryRequest, auth=Depends(get_project_auth("erp"))):
    """
    Process ERP queries with real tenant data.
    
    Request body:
    - query: Natural language question
    - tenant_id: Tenant identifier
    - context: Landing page info, tenant settings, etc.
    - data: REAL ERP data (invoices, products, customers, etc.)
    """
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
async def file_extract(request: FileExtractRequest, auth=Depends(get_project_auth("erp"))):
    """
    Extract text from uploaded files (PDF, images, spreadsheets).
    
    Request body:
    - tenant_id: Tenant identifier
    - filename: Original filename
    - file_type: pdf, image, spreadsheet, text
    """
    result = await erp_file_service.extract_text(
        tenant_id=request.tenant_id,
        filename=request.filename,
        file_type=request.file_type,
    )
    return {"success": True, "data": result}


# ================================================================================================
# PROACTIVE ALERTS
# ================================================================================================

@router.post("/alert/analyze")
async def alert_analyze(request: AlertAnalyzeRequest, auth=Depends(get_project_auth("erp"))):
    """
    Analyze ERP data for proactive alerts.
    
    Request body:
    - tenant_id: Tenant identifier
    - data: ERP data to analyze for alerts (inventory, invoices, etc.)
    """
    result = await erp_alert_service.analyze(
        tenant_id=request.tenant_id,
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# USAGE STATISTICS
# ================================================================================================

@router.get("/stats")
async def stats(auth=Depends(get_project_auth("erp"))):
    """Get per-tenant usage statistics."""
    result = await erp_stats_service.get_stats()
    return {"success": True, "data": result}


# ================================================================================================
# HEALTH CHECK
# ================================================================================================

@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"success": True, "data": {"status": "healthy", "service": "erp_gateway"}}