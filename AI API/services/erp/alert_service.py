# ====================================================================================================
# HDM AI Engine - services/erp/alert_service.py
# Stateless — MERN stores alerts, Python does AI only
# ====================================================================================================

from typing import Dict, Any
from services.ai_service import ai_service
from loguru import logger
import json


class ERPAlertService:
    async def analyze(self, tenant_id: str, data: dict = None) -> Dict[str, Any]:
        if not data:
            return {"alerts": [], "severity": "low", "message": "No data provided."}

        parts = ["Find issues in this business data and return alerts as JSON.", ""]

        products = data.get("products", data.get("inventory", []))
        if products:
            parts.append("INVENTORY:")
            low_count = 0
            for item in products:
                stock = item.get("stock", 0)
                reorder = item.get("reorderLevel", item.get("reorder_level", 10))
                name = item.get("name", item.get("product", "?"))
                if stock == 0:
                    parts.append(f"  {name}: {stock} units (reorder at {reorder}) ← OUT OF STOCK")
                    low_count += 1
                elif stock <= reorder:
                    parts.append(f"  {name}: {stock} units (reorder at {reorder}) ← LOW")
                    low_count += 1
                else:
                    parts.append(f"  {name}: {stock} units (reorder at {reorder})")
            parts.append(f"  → {low_count} items low/out of stock\n")

        if "invoices" in data:
            parts.append("INVOICES:")
            overdue_count = 0
            for inv in data["invoices"]:
                status = inv.get("status", "")
                is_problem = status in ["overdue", "sent", "unpaid"]
                marker = " ← OVERDUE" if is_problem else ""
                if is_problem:
                    overdue_count += 1
                parts.append(f"  {inv.get('number','?')}: {inv.get('customer','?')} — {inv.get('amount',0)} ({status}){marker}")
            parts.append(f"  → {overdue_count} unpaid/overdue invoices\n")

        if "bills" in data:
            parts.append("BILLS:")
            for bill in data["bills"]:
                parts.append(f"  {bill.get('number','?')}: {bill.get('supplier','?')} — {bill.get('amount',0)} ({bill.get('status','?')})")
            parts.append("")

        if "salesOrders" in data:
            pending = [o for o in data["salesOrders"] if o.get("status") in ["processing", "pending"]]
            if pending:
                parts.append("PENDING ORDERS:")
                for order in pending:
                    parts.append(f"  {order.get('number','?')}: {order.get('customer','?')} — {order.get('total',0)} ({order.get('status','?')})")
                parts.append(f"  → {len(pending)} orders pending\n")

        if "purchaseOrders" in data:
            pending_po = [o for o in data["purchaseOrders"] if o.get("status") in ["sent", "pending"]]
            if pending_po:
                parts.append("PENDING PURCHASE ORDERS:")
                for order in pending_po:
                    parts.append(f"  {order.get('number','?')}: {order.get('supplier','?')} — {order.get('total',0)}")
                parts.append("")

        if "workOrders" in data:
            processing = [w for w in data["workOrders"] if w.get("status") == "processing"]
            if processing:
                parts.append("WORK ORDERS IN PROGRESS:")
                for wo in processing:
                    parts.append(f"  {wo.get('number','?')}: {wo.get('product','?')} x{wo.get('quantity',0)}")
                parts.append("")

        parts.append("""Return ONLY valid JSON (no markdown, no backticks):
{
    "alerts": [
        {"type": "low_stock/out_of_stock/overdue_invoice/pending_order", "message": "what and why", "severity": "critical/warning/info"}
    ],
    "severity": "low/warning/critical"
}
Rules:
- critical = out of stock OR invoice 30+ days overdue
- warning = low stock OR overdue invoice OR pending order
- info = everything else
- Include ALL issues found above
- Use real names and numbers""")

        prompt = "\n".join(parts)
        result = await ai_service.groq_chat(
            [{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
            module="erp",
        )

        try:
            text = result.get("reply", "{}").replace("```json", "").replace("```", "").strip()
            alerts_data = json.loads(text)
            alerts = alerts_data.get("alerts", [])
            severity = alerts_data.get("severity", "low")

            logger.info(f"Alerts: {len(alerts)} alerts, severity={severity}")
            return {"alerts": alerts, "severity": severity, "data_analyzed": True}
        except Exception as e:
            logger.error(f"Alert parsing failed: {e}")
            return {"alerts": [], "severity": "low", "data_analyzed": True}


erp_alert_service = ERPAlertService()