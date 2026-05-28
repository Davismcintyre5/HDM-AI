# ====================================================================================================
# 7. server/services/vault/command_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from loguru import logger
import json

class VaultCommandService:
    INTENTS = [
        "generate_password", "show_weak_passwords", "show_breaches",
        "show_devices", "enable_2fa", "run_scan", "backup_now", "check_license",
    ]

    async def execute(self, user_id: str, command: str, data: dict = None) -> Dict[str, Any]:
        context_str = ""
        if data:
            context_str = f"\nUser data: {json.dumps(data, indent=2)[:1500]}"

        prompt = f"""You are a cybersecurity command executor. Available commands: {', '.join(self.INTENTS)}.
User command: "{command}"{context_str}

Return JSON:
{{"intent": "one of the above", "success": true/false, "result": "what to tell the user based on their real data"}}

If the command intent is 'generate_password', return a strong password suggestion.
If it's 'show_weak_passwords', list them from the user data.
If it's 'show_breaches', list breaches from the user data.
Always use real data when available. Do not invent data."""
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=300)
        try:
            return json.loads(result.get("reply", "{}"))
        except:
            return {"intent": "", "success": False, "result": "Could not understand command. Try: generate password, run scan, check breaches."}


vault_command_service = VaultCommandService()