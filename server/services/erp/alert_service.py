# ====================================================================================================
# server/services/erp/alert_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.erp.alert_schedule import AlertSchedule
from loguru import logger

class ERPAlertService:
    async def analyze(self, tenant_id: str, data: dict = None) -> Dict[str, Any]:
        prompt = f"Analyze this ERP data for proactive alerts: {data}. Return JSON: {{\"alerts\": [{{\"type\": \"...\", \"message\": \"...\", \"severity\": \"low|medium|high\"}}]}}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=500)
        try:
            import json
            alerts_data = json.loads(result.get("reply", "{}"))
            alerts = []
            for a in alerts_data.get("alerts", []):
                await AlertSchedule(tenant_id=tenant_id, alert_type=a["type"], message=a["message"], severity=a.get("severity", "low")).insert()
                alerts.append(a)
            return {"alerts": alerts, "severity": max((a.get("severity", "low") for a in alerts), key=lambda s: ["low","medium","high"].index(s)) if alerts else "low"}
        except:
            return {"alerts": [], "severity": "low"}

erp_alert_service = ERPAlertService()