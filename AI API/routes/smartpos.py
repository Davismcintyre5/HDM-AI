from fastapi import APIRouter
from schemas.smartpos.chat import ChatRequest
from schemas.smartpos.command import CommandRequest
from schemas.smartpos.analytics import AnalyticsRequest
from schemas.smartpos.forecast import ForecastRequest
from schemas.smartpos.insights import InsightsRequest
from schemas.smartpos.alerts import AlertCheckRequest
from schemas.smartpos.anomaly import AnomalyRequest
from schemas.smartpos.report import ReportRequest
from schemas.smartpos.search import SearchRequest
from schemas.smartpos.admin import AdminChatRequest
from services.smartpos.chat_service import smartpos_chat_service
from services.smartpos.command_service import command_service
from services.smartpos.analytics_service import analytics_service
from services.smartpos.forecast_service import forecast_service
from services.smartpos.insights_service import insights_service
from services.smartpos.alerts_service import alerts_service
from services.smartpos.anomaly_service import anomaly_service
from services.smartpos.report_service import report_service
from services.smartpos.search_service import search_service
from services.smartpos.admin_service import admin_service

router = APIRouter(prefix="/smartpos", tags=["SmartPOS AI"])

@router.post("/public/chat")
async def public_chat(request: ChatRequest):
    result = await smartpos_chat_service.chat(client_id=request.client_id, message=request.message, feature="public", data=request.data)
    return {"success": True, "data": result}

@router.post("/chat")
async def chat(request: ChatRequest):
    result = await smartpos_chat_service.chat(client_id=request.client_id, message=request.message, messages=request.messages, business_id=request.business_id, feature=request.feature, data=request.data)
    return {"success": True, "data": result}

@router.post("/command")
async def command(request: CommandRequest):
    result = await command_service.execute(business_id=request.business_id, command=request.command, parameters=request.parameters)
    return {"success": True, "data": result}

@router.post("/analytics/sales")
async def analytics_sales(request: AnalyticsRequest):
    result = await analytics_service.analyze(business_id=request.business_id, analytics_type="sales", period=request.period, data=request.data, filters=request.filters)
    return {"success": True, "data": result}

@router.post("/analytics/products")
async def analytics_products(request: AnalyticsRequest):
    result = await analytics_service.analyze(business_id=request.business_id, analytics_type="products", period=request.period, data=request.data)
    return {"success": True, "data": result}

@router.post("/analytics/customers")
async def analytics_customers(request: AnalyticsRequest):
    result = await analytics_service.analyze(business_id=request.business_id, analytics_type="customers", period=request.period, data=request.data)
    return {"success": True, "data": result}

@router.post("/analytics/employees")
async def analytics_employees(request: AnalyticsRequest):
    result = await analytics_service.analyze(business_id=request.business_id, analytics_type="employees", period=request.period, data=request.data)
    return {"success": True, "data": result}

@router.post("/forecast/restock")
async def forecast_restock(request: ForecastRequest):
    result = await forecast_service.forecast(business_id=request.business_id, forecast_type="restock", period=request.period, data=request.data, product_ids=request.product_ids)
    return {"success": True, "data": result}

@router.post("/forecast/trends")
async def forecast_trends(request: ForecastRequest):
    result = await forecast_service.forecast(business_id=request.business_id, forecast_type="trends", period=request.period, data=request.data)
    return {"success": True, "data": result}

@router.post("/insights/profit")
async def insights_profit(request: InsightsRequest):
    result = await insights_service.get_insights(business_id=request.business_id, insight_type="profit", data=request.data)
    return {"success": True, "data": result}

@router.post("/insights/tax")
async def insights_tax(request: InsightsRequest):
    result = await insights_service.get_insights(business_id=request.business_id, insight_type="tax", data=request.data)
    return {"success": True, "data": result}

@router.post("/alerts/check")
async def alerts_check(request: AlertCheckRequest):
    result = await alerts_service.check_alerts(business_id=request.business_id, data=request.data, alert_types=request.alert_types)
    return {"success": True, "data": result}

@router.post("/anomaly/detect")
async def anomaly_detect(request: AnomalyRequest):
    result = await anomaly_service.detect(business_id=request.business_id, data=request.data)
    return {"success": True, "data": result}

@router.post("/report/generate")
async def report_generate(request: ReportRequest):
    result = await report_service.generate(business_id=request.business_id, report_type=request.report_type, period=request.period)
    return {"success": True, "data": result}

@router.post("/search/semantic")
async def search_semantic(request: SearchRequest):
    result = await search_service.search(business_id=request.business_id, query=request.query, limit=request.limit)
    return {"success": True, "data": result}

@router.post("/admin/chat")
async def admin_chat(request: AdminChatRequest):
    result = await admin_service.chat(message=request.message, messages=None)
    return {"success": True, "data": result}

@router.get("/health")
async def health():
    return {"success": True, "data": {"status": "healthy", "service": "smartpos"}}