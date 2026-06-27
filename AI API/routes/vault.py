from fastapi import APIRouter
from schemas.vault.chat import ChatRequest
from schemas.vault.security import SecurityOverviewRequest, SecurityAlertRequest
from schemas.vault.command import CommandRequest
from schemas.vault.report import ReportGenerateRequest, ReportScheduleRequest
from services.vault.chat_service import vault_chat_service
from services.vault.security_service import vault_security_service
from services.vault.command_service import vault_command_service
from services.vault.report_service import vault_report_service

router = APIRouter(prefix="/vault", tags=["Vault AI"])

@router.post("/public/chat")
async def public_chat(request: ChatRequest):
    result = await vault_chat_service.chat(user_id=request.user_id, message=request.message, feature="public", data=request.data)
    return {"success": True, "data": result}

@router.post("/chat")
async def private_chat(request: ChatRequest):
    result = await vault_chat_service.chat(user_id=request.user_id, message=request.message, feature="private", data=request.data)
    return {"success": True, "data": result}

@router.post("/security/overview")
async def security_overview(request: SecurityOverviewRequest):
    result = await vault_security_service.overview(user_id=request.user_id, include_details=request.include_details, data=request.data)
    return {"success": True, "data": result}

@router.post("/security/alerts")
async def security_alerts(request: SecurityAlertRequest):
    result = await vault_security_service.alerts(user_id=request.user_id, severity_filter=request.severity_filter, data=request.data)
    return {"success": True, "data": result}

@router.post("/command")
async def command(request: CommandRequest):
    result = await vault_command_service.execute(user_id=request.user_id, command=request.command, data=request.data)
    return {"success": True, "data": result}

@router.post("/report/generate")
async def report_generate(request: ReportGenerateRequest):
    result = await vault_report_service.generate(user_id=request.user_id, report_type=request.report_type, data=request.data)
    return {"success": True, "data": result}

@router.post("/report/schedule")
async def report_schedule(request: ReportScheduleRequest):
    result = await vault_report_service.schedule(user_id=request.user_id, report_type=request.report_type, webhook_url=request.webhook_url, frequency=request.frequency, data=request.data)
    return {"success": True, "data": result}

@router.get("/health")
async def health():
    return {"success": True, "data": {"status": "healthy"}}