# ====================================================================================================
# HDM AI Engine - services/vault/chat_service.py
# ====================================================================================================

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

        return {"reply": reply, "tokens_used": result.get("tokens_used", 0), "model": result.get("model", "")}

    def _build_system_prompt(self, feature: str, data: Optional[dict] = None) -> str:
        if feature == "public":
            base = (
                "You are NexGuard AI, the official assistant for NexGuard — "
                "a next-generation cybersecurity suite providing real-time protection, "
                "deep scanning, firewall, VPN, device management, and threat intelligence.\n\n"
                "NEXGUARD CORE FEATURES:\n"
                "- Real-Time File Protection\n- Deep Scanning Engine\n- Firewall Manager\n"
                "- Secure VPN\n- Secure Vault\n- Device & License Management\n"
                "- Threat Intelligence\n- System Monitoring\n\n"
                "PLATFORMS: Windows, macOS, Linux, Web Dashboard\n\n"
                "PLANS: Free Trial (30 days), Pro, Enterprise\n\n"
            )
            if data:
                base += "--- NEXGUARD CUSTOM INFORMATION (use this exact data) ---\n"
                if data.get("features"):
                    if isinstance(data["features"], list):
                        base += "\nFEATURES:\n" + "\n".join([f"  • {f}" for f in data["features"]])
                    else:
                        base += f"\nFeatures: {data['features']}\n"
                if data.get("pricing"):
                    base += f"\n⚠️ EXACT PRICING:\n{data['pricing']}\n"
                if data.get("support"):
                    s = data["support"]
                    base += "\nSUPPORT:\n"
                    if isinstance(s, dict):
                        if s.get("email"): base += f"  • Email: {s['email']}\n"
                        if s.get("phone"): base += f"  • Phone: {s['phone']}\n"
                base += "\n⚠️ Use ONLY the exact information above. Do not invent.\n"
            else:
                base += "\nEncourage visitors to start a 30-day free trial or contact support.\n"
            return base
        else:
            base = "You are NexGuard AI assistant for Pro users. Provide detailed cybersecurity advice, scan analysis, and security recommendations."
            if data and "user" in data:
                user = data["user"]
                base += f"""
REAL USER SECURITY DATA:
- License: {user.get('license_key','N/A')}
- Devices Protected: {user.get('devices_count','?')}
- Threats Detected: {user.get('threats_detected','?')}
- Last Full Scan: {user.get('last_scan','Never')}
- Firewall Status: {user.get('firewall_enabled','Disabled')}
- VPN Status: {user.get('vpn_connected','Disconnected')}
- Plan: {user.get('plan','Free Trial')}
Use this real data to give personalized advice. Do not make up numbers."""
            else:
                base += "\n\nNo device data provided. Tell user to connect their NexGuard agent."
            return base

vault_chat_service = VaultChatService()