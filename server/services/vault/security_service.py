# ====================================================================================================
# 6. server/services/vault/security_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.vault.security_scan import SecurityScan
from loguru import logger
import json

class VaultSecurityService:
    async def overview(self, user_id: str, include_details: bool = True, data: dict = None) -> Dict[str, Any]:
        if not data:
            return {"score": 0, "summary": "No security data provided. Connect your Vault account to get a real security overview.", "findings": [], "recommendations": []}

        context = json.dumps(data, indent=2)[:3000]
        prompt = f"""You are a cybersecurity expert. Analyze this REAL security data and provide an overview.

User Security Data:
{context}

Return JSON with:
- score: 0-100 overall security score
- summary: brief summary of security posture
- findings: list of specific security issues found
- recommendations: actionable steps to improve security (ordered by priority)
"""
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=800)
        try:
            parsed = json.loads(result.get("reply", "{}"))
            # Cache the scan
            await SecurityScan(
                user_id=user_id,
                scan_type="overview",
                score=parsed.get("score", 0),
                findings=parsed.get("findings", []),
                recommendations=parsed.get("recommendations", []),
            ).insert()
            return parsed
        except:
            return {"score": 50, "summary": "Scan completed, but analysis failed. Please try again.", "findings": [], "recommendations": []}

    async def alerts(self, user_id: str, severity_filter: str = None, data: dict = None) -> Dict[str, Any]:
        if not data or "current_threats" not in data:
            return {"alerts": [], "has_critical": False}

        threats = data["current_threats"]
        if severity_filter:
            threats = [t for t in threats if t.get("severity") == severity_filter]

        return {
            "alerts": threats,
            "has_critical": any(t.get("severity") == "critical" for t in threats),
        }


vault_security_service = VaultSecurityService()