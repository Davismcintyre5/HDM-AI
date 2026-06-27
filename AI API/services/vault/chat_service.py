from typing import Dict, Any, Optional
from services.ai_service import ai_service
import json

class VaultChatService:
    MAX_HISTORY = 15

    async def chat(self, user_id: str, message: str, messages: Optional[list] = None, feature: str = "public", data: Optional[dict] = None) -> Dict[str, Any]:
        history = messages or []
        history.append({"role": "user", "content": message})

        system_prompt = self._build_system_prompt(feature, data)
        history.insert(0, {"role": "system", "content": system_prompt})

        result = await ai_service.groq_chat(history, max_tokens=800, module="vault")
        reply = result.get("reply", "Sorry, I couldn't process that.")

        return {"reply": reply, "tokens_used": result.get("tokens_used", 0)}

    def _build_system_prompt(self, feature: str, data: Optional[dict] = None) -> str:
        if feature == "public":
            base = (
                "You are HDM Vault AI, the official assistant for HDM Vault — a password manager and cybersecurity platform.\n\n"
                "HDM Vault helps users:\n"
                "- Store passwords securely with AES-256 encryption\n"
                "- Check if accounts have been breached in data leaks\n"
                "- Monitor device security status\n"
                "- Generate strong, unique passwords\n"
                "- Enable Two-Factor Authentication (2FA)\n"
                "- Run security scans and get reports\n\n"
            )
            if data:
                base += "--- HDM VAULT INFORMATION (use this exact data) ---\n"
                if data.get("features"):
                    if isinstance(data["features"], list):
                        base += "\nFEATURES:\n" + "\n".join([f"  • {f}" for f in data["features"]])
                    else:
                        base += f"\nFeatures: {data['features']}\n"
                if data.get("pricing"):
                    base += f"""
⚠️ EXACT PRICING — USE THESE NUMBERS ONLY:
{data['pricing']}

Repeat the exact numbers above when asked about pricing. Do not invent smaller numbers.
"""
                if data.get("support"):
                    s = data["support"]
                    base += "\nSUPPORT:\n"
                    if isinstance(s, dict):
                        if s.get("email"): base += f"  • Email: {s['email']}\n"
                        if s.get("phone"): base += f"  • Phone: {s['phone']}\n"
                        if s.get("hours"): base += f"  • Hours: {s['hours']}\n"
                    else:
                        base += f"  {s}\n"
                if data.get("free_trial"):
                    base += f"\nFree Trial: {data['free_trial']}\n"
                base += "\n⚠️ Use ONLY the exact information above. Do not invent features, pricing, or details.\n"
            else:
                base += "\nEncourage visitors to sign up for a free trial or contact support.\n"
            return base
        else:
            base = "You are HDM Vault AI assistant for Pro users. Provide detailed cybersecurity advice, scan analysis, and security recommendations."
            if data and "user" in data:
                user = data["user"]
                base += f"""

REAL USER SECURITY DATA:
- Total Passwords: {user.get('total_passwords','?')}
- Weak Passwords: {user.get('weak_passwords','?')}
- Reused Passwords: {user.get('reused_passwords','?')}
- Breached Accounts: {user.get('breached_accounts','?')}
- 2FA Enabled: {user.get('two_factor_enabled',False)}
- Security Score: {user.get('security_score','?')}/100
- Last Full Scan: {user.get('last_full_scan','Never')}
- Devices: {json.dumps(user.get('devices',[]))}

Use this real security data to give personalized advice. Do not make up numbers."""
            else:
                base += "\n\nNo security data provided. Tell user to connect their Vault account."
            return base

vault_chat_service = VaultChatService()