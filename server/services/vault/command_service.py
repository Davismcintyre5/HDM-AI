# ====================================================================================================
# server/services/vault/command_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from loguru import logger

class VaultCommandService:
    INTENTS = ["generate_password", "show_weak_passwords", "show_breaches", "show_devices", "enable_2fa", "run_scan", "backup_now", "check_license"]

    async def execute(self, user_id: str, command: str) -> Dict[str, Any]:
        prompt = f"""You are a cybersecurity command executor. Available commands: {', '.join(self.INTENTS)}.
User command: "{command}"
Return JSON: {{"intent": "one of the above", "success": true/false, "result": "what to tell the user"}}"""
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=300)
        try:
            import json
            data = json.loads(result.get("reply", "{}"))
            return {"intent": data.get("intent", ""), "success": data.get("success", True), "result": data.get("result", "Command executed.")}
        except:
            return {"intent": "", "success": False, "result": "Could not understand command. Try: generate password, run scan, check breaches."}

vault_command_service = VaultCommandService()