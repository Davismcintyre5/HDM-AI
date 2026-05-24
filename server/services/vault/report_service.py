# ====================================================================================================
# server/services/vault/report_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.vault.report import VaultReport
from loguru import logger

class VaultReportService:
    async def generate(self, user_id: str, report_type: str = "security_overview") -> Dict[str, Any]:
        prompt = f"Generate a detailed {report_type} cybersecurity report. Include: Executive Summary, Findings, Risk Assessment, Recommendations. Format professionally."
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.4, max_tokens=1500)
        report = VaultReport(user_id=user_id, report_type=report_type, content=result.get("reply", ""))
        await report.insert()
        return {"report_id": str(report.id), "content": result.get("reply", ""), "format": "text"}

    async def schedule(self, user_id: str, report_type: str, webhook_url: str, frequency: str = "weekly") -> Dict[str, Any]:
        logger.info(f"Report scheduled: {report_type}, frequency={frequency}, webhook={webhook_url}")
        return {"scheduled": True, "report_type": report_type, "frequency": frequency, "webhook_url": webhook_url}

vault_report_service = VaultReportService()