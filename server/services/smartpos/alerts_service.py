# ====================================================================================================
# 11. server/services/smartpos/alerts_service.py
# ====================================================================================================
from typing import Dict, Any, List
from models.smartpos.alert import Alert
from services.ai_service import ai_service
from datetime import datetime
from loguru import logger
import json

class AlertsService:
    async def check_alerts(self, business_id: str, data: dict = None, alert_types: List[str] = None) -> Dict[str, Any]:
        if not data:
            return {"alerts": [], "has_critical": False, "message": "No data provided. Send inventory/sales data for alert checking."}

        parts = ["You are a POS monitoring AI. Analyze this REAL data and generate proactive alerts. Only flag REAL issues.", "", "--- REAL INVENTORY & SALES DATA ---"]
        if "inventory" in data:
            parts.append(f"\nINVENTORY ({len(data['inventory'])} items):")
            for item in data["inventory"][:20]:
                stock = item.get("stock", 0); reorder = item.get("reorder_level", 10)
                status = "⚠️ LOW" if stock <= reorder else "✓ OK"
                parts.append(f"  {status} | {item.get('product', item.get('name','?'))}: {stock} units (reorder at {reorder})")
        if "unusual_transactions" in data:
            parts.append(f"\nUNUSUAL TRANSACTIONS:")
            for t in data["unusual_transactions"][:10]:
                parts.append(f"  • ID {t.get('id','?')}: {t.get('amount',0)} at {t.get('time','?')} by {t.get('cashier','?')}")
        parts.append('\n\nReturn JSON: {"alerts": [{"type": "...", "message": "specific alert with real data", "severity": "info/warning/critical"}]}')
        parts.append("⚠️ Use specific product names and numbers from the data above.")

        prompt = "\n".join(parts)
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=400, service="smartpos")
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