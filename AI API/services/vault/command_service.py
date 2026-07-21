from typing import Dict, Any
from services.ai_service import ai_service
import json

class VaultCommandService:
    INTENTS = [
        "run_scan", "check_threats", "toggle_firewall", "connect_vpn",
        "disconnect_vpn", "quarantine_file", "restore_file", "check_license",
        "add_device", "remove_device", "generate_report", "view_alerts"
    ]

    async def execute(self, user_id: str, command: str, data: dict = None) -> Dict[str, Any]:
        context_str = json.dumps(data, indent=2)[:1500] if data else ""
        prompt = f"""You are NexGuard command executor. Available: {', '.join(self.INTENTS)}.
User command: "{command}"
{context_str}
Return JSON: {{"intent": "...", "success": true/false, "result": "what to tell the user"}}"""
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=300, module="vault")
        try:
            return json.loads(result.get("reply", "{}"))
        except:
            return {"intent": "", "success": False, "result": "Could not understand command."}

vault_command_service = VaultCommandService()