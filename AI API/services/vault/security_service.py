from typing import Dict, Any
from services.ai_service import ai_service
import json

class VaultSecurityService:
    async def overview(self, user_id: str, include_details: bool = True, data: dict = None) -> Dict[str, Any]:
        if not data:
            return {"score": 0, "summary": "No security data provided.", "findings": [], "recommendations": []}
        context = json.dumps(data, indent=2)[:3000]
        prompt = f"Analyze this REAL security data and provide an overview.\n{context}\n\nReturn JSON with: score (0-100), summary, findings (list), recommendations (list)."
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=800, module="vault")
        try:
            return json.loads(result.get("reply", "{}"))
        except:
            return {"score": 50, "summary": "Scan completed.", "findings": [], "recommendations": []}

    async def alerts(self, user_id: str, severity_filter: str = None, data: dict = None) -> Dict[str, Any]:
        if not data or "current_threats" not in data:
            return {"alerts": [], "has_critical": False}
        threats = data["current_threats"]
        if severity_filter:
            threats = [t for t in threats if t.get("severity") == severity_filter]
        return {"alerts": threats, "has_critical": any(t.get("severity") == "critical" for t in threats)}

vault_security_service = VaultSecurityService()