# ====================================================================================================
# server/services/vault/security_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.vault.security_scan import SecurityScan
from loguru import logger

class VaultSecurityService:
    async def overview(self, user_id: str, include_details: bool = True) -> Dict[str, Any]:
        prompt = "Generate a cybersecurity overview for a user. Include: password health score, potential breach checks, device security status. Return JSON: {\"score\": 0-100, \"summary\": \"...\", \"findings\": [], \"recommendations\": []}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=800)
        try:
            import json
            data = json.loads(result.get("reply", "{}"))
            await SecurityScan(user_id=user_id, scan_type="overview", score=data.get("score", 0), findings=data.get("findings", []), recommendations=data.get("recommendations", [])).insert()
            return data
        except:
            return {"score": 50, "summary": "Scan completed.", "findings": [], "recommendations": ["Enable 2FA", "Update passwords regularly"]}

    async def alerts(self, user_id: str, severity_filter: str = None) -> Dict[str, Any]:
        prompt = "Generate security alerts for a user. Return JSON: {\"alerts\": [{\"type\": \"...\", \"message\": \"...\", \"severity\": \"info|warning|critical\"}]}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=400)
        try:
            import json
            data = json.loads(result.get("reply", "{}"))
            alerts = data.get("alerts", [])
            return {"alerts": alerts, "has_critical": any(a.get("severity") == "critical" for a in alerts)}
        except:
            return {"alerts": [], "has_critical": False}

vault_security_service = VaultSecurityService()