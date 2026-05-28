# ====================================================================================================
# 9. server/routes/vault.py — COMPLETE (8 endpoints)
# ====================================================================================================
from fastapi import APIRouter, Depends
from middleware.auth import get_project_auth
from schemas.vault.chat import ChatRequest
from schemas.vault.security import SecurityOverviewRequest, SecurityAlertRequest
from schemas.vault.command import CommandRequest
from schemas.vault.report import ReportGenerateRequest, ReportScheduleRequest
from services.vault.chat_service import vault_chat_service
from services.vault.security_service import vault_security_service
from services.vault.command_service import vault_command_service
from services.vault.report_service import vault_report_service

router = APIRouter(prefix="/vault", tags=["Vault AI"])
A = Depends(get_project_auth("vault"))

@router.post("/public/chat")
async def public_chat(request: ChatRequest, auth=A):
    result = await vault_chat_service.chat(request.user_id, request.message, request.conversation_id, "public", request.data)
    return {"success": True, "data": result}

@router.post("/chat")
async def private_chat(request: ChatRequest, auth=A):
    result = await vault_chat_service.chat(request.user_id, request.message, request.conversation_id, "private", request.data)
    return {"success": True, "data": result}

@router.post("/security/overview")
async def security_overview(request: SecurityOverviewRequest, auth=A):
    result = await vault_security_service.overview(request.user_id, request.include_details, request.data)
    return {"success": True, "data": result}

@router.post("/security/alerts")
async def security_alerts(request: SecurityAlertRequest, auth=A):
    result = await vault_security_service.alerts(request.user_id, request.severity_filter, request.data)
    return {"success": True, "data": result}

@router.post("/command")
async def command(request: CommandRequest, auth=A):
    result = await vault_command_service.execute(request.user_id, request.command, request.data)
    return {"success": True, "data": result}

@router.post("/report/generate")
async def report_generate(request: ReportGenerateRequest, auth=A):
    result = await vault_report_service.generate(request.user_id, request.report_type, request.data)
    return {"success": True, "data": result}

@router.post("/report/schedule")
async def report_schedule(request: ReportScheduleRequest, auth=A):
    result = await vault_report_service.schedule(request.user_id, request.report_type, request.webhook_url, request.frequency, request.data)
    return {"success": True, "data": result}

@router.get("/health")
async def health():
    return {"success": True, "data": {"status": "healthy"}}