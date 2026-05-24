# ====================================================================================================
# server/services/smartpos/alerts_service.py
# ====================================================================================================
from typing import Dict, Any, List
from models.smartpos.alert import Alert
from services.ai_service import ai_service
from datetime import datetime
from loguru import logger
import json

class AlertsService:
    async def check_alerts(self, business_id: str, data: dict = None, alert_types: List[str] = None) -> Dict[str, Any]:
        if data:
            prompt = f"""You are a POS monitoring AI. Analyze this REAL inventory/sales data for alerts.

Data: {json.dumps(data)[:3000]}
Alert types to check: {', '.join(alert_types) if alert_types else 'all'}

Return JSON: {{"alerts": [{{"type": "low_stock/unusual_activity/...", "message": "specific alert", "severity": "info/warning/critical"}}]}}"""
        else:
            return {"alerts": [], "has_critical": False, "message": "No data provided. Send inventory/sales data for alert checking."}

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=400)
        try:
            parsed = json.loads(result.get("reply", "{}"))
            alerts = []
            for a in parsed.get("alerts", []):
                alert = Alert(business_id=business_id, type=a["type"], message=a["message"], severity=a.get("severity", "info"))
                await alert.insert()
                alerts.append({"type": a["type"], "message": a["message"], "severity": a.get("severity", "info")})
            return {"alerts": alerts, "has_critical": any(a["severity"] == "critical" for a in alerts)}
        except:
            return {"alerts": [], "has_critical": False}

alerts_service = AlertsService()