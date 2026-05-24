# ====================================================================================================
# server/routes/smartpos.py — COMPLETE (16 endpoints)
# ====================================================================================================
"""
HDM AI - SmartPOS AI Routes
All endpoints require project API key authentication
"""

from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import get_project_auth
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
A = Depends(get_project_auth("smartpos"))


# ================================================================================================
# PUBLIC CHAT (Landing Page)
# ================================================================================================

@router.post("/public/chat")
async def public_chat(request: ChatRequest, auth=Depends(get_project_auth("smartpos"))):
    """Landing page chatbot — general POS questions, no business data needed."""
    result = await smartpos_chat_service.chat(
        client_id=request.client_id,
        message=request.message,
        conversation_id=request.conversation_id,
        feature="public",
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# CLIENT DASHBOARD CHAT
# ================================================================================================

@router.post("/chat")
async def chat(request: ChatRequest, auth=A):
    """Client dashboard AI — send real business data for accurate responses."""
    result = await smartpos_chat_service.chat(
        client_id=request.client_id,
        message=request.message,
        conversation_id=request.conversation_id,
        business_id=request.business_id,
        feature="chat",
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# NLP COMMANDS
# ================================================================================================

@router.post("/command")
async def command(request: CommandRequest, auth=A):
    """Natural language commands for POS operations."""
    result = await command_service.execute(
        business_id=request.business_id,
        command=request.command,
        parameters=request.parameters,
    )
    return {"success": True, "data": result}


# ================================================================================================
# ANALYTICS
# ================================================================================================

@router.post("/analytics/sales")
async def analytics_sales(request: AnalyticsRequest, auth=A):
    """Analyze real sales data — requires data field."""
    result = await analytics_service.analyze(
        business_id=request.business_id,
        analytics_type="sales",
        period=request.period,
        data=request.data,
        filters=request.filters,
    )
    return {"success": True, "data": result}


@router.post("/analytics/products")
async def analytics_products(request: AnalyticsRequest, auth=A):
    """Analyze real product data — requires data field."""
    result = await analytics_service.analyze(
        business_id=request.business_id,
        analytics_type="products",
        period=request.period,
        data=request.data,
    )
    return {"success": True, "data": result}


@router.post("/analytics/customers")
async def analytics_customers(request: AnalyticsRequest, auth=A):
    """Analyze real customer data — requires data field."""
    result = await analytics_service.analyze(
        business_id=request.business_id,
        analytics_type="customers",
        period=request.period,
        data=request.data,
    )
    return {"success": True, "data": result}


@router.post("/analytics/employees")
async def analytics_employees(request: AnalyticsRequest, auth=A):
    """Analyze real employee data — requires data field."""
    result = await analytics_service.analyze(
        business_id=request.business_id,
        analytics_type="employees",
        period=request.period,
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# FORECASTING
# ================================================================================================

@router.post("/forecast/restock")
async def forecast_restock(request: ForecastRequest, auth=A):
    """Restock suggestions based on real inventory data."""
    result = await forecast_service.forecast(
        business_id=request.business_id,
        forecast_type="restock",
        period=request.period,
        data=request.data,
        product_ids=request.product_ids,
    )
    return {"success": True, "data": result}


@router.post("/forecast/trends")
async def forecast_trends(request: ForecastRequest, auth=A):
    """Trend detection based on real historical data."""
    result = await forecast_service.forecast(
        business_id=request.business_id,
        forecast_type="trends",
        period=request.period,
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# INSIGHTS
# ================================================================================================

@router.post("/insights/profit")
async def insights_profit(request: InsightsRequest, auth=A):
    """Profit analysis — requires real financial data."""
    result = await insights_service.get_insights(
        business_id=request.business_id,
        insight_type="profit",
        data=request.data,
    )
    return {"success": True, "data": result}


@router.post("/insights/tax")
async def insights_tax(request: InsightsRequest, auth=A):
    """Tax reporting — requires real tax data."""
    result = await insights_service.get_insights(
        business_id=request.business_id,
        insight_type="tax",
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# PROACTIVE ALERTS
# ================================================================================================

@router.post("/alerts/check")
async def alerts_check(request: AlertCheckRequest, auth=A):
    """Check for low stock, unusual activity, and other alerts."""
    result = await alerts_service.check_alerts(
        business_id=request.business_id,
        data=request.data,
        alert_types=request.alert_types,
    )
    return {"success": True, "data": result}


# ================================================================================================
# ANOMALY DETECTION
# ================================================================================================

@router.post("/anomaly/detect")
async def anomaly_detect(request: AnomalyRequest, auth=A):
    """Detect anomalies in transaction data."""
    result = await anomaly_service.detect(
        business_id=request.business_id,
        data=request.data,
    )
    return {"success": True, "data": result}


# ================================================================================================
# REPORT GENERATION
# ================================================================================================

@router.post("/report/generate")
async def report_generate(request: ReportRequest, auth=A):
    """Generate business reports."""
    result = await report_service.generate(
        business_id=request.business_id,
        report_type=request.report_type,
        period=request.period,
    )
    return {"success": True, "data": result}


# ================================================================================================
# SEMANTIC SEARCH
# ================================================================================================

@router.post("/search/semantic")
async def search_semantic(request: SearchRequest, auth=A):
    """Semantic search across business data."""
    result = await search_service.search(
        business_id=request.business_id,
        query=request.query,
        limit=request.limit,
    )
    return {"success": True, "data": result}


# ================================================================================================
# ADMIN PANEL CHAT
# ================================================================================================

@router.post("/admin/chat")
async def admin_chat(request: AdminChatRequest, auth=A):
    """Admin panel AI assistant."""
    result = await admin_service.chat(
        message=request.message,
        conversation_id=request.conversation_id,
    )
    return {"success": True, "data": result}