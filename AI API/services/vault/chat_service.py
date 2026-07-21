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
                "You are NexGuard AI, the official assistant for NexGuard — "
                "a next-generation cybersecurity suite providing real-time protection, "
                "deep scanning, firewall, VPN, device management, and threat intelligence.\n\n"
                "NEXGUARD CORE FEATURES:\n"
                "- Real-Time File Protection (monitors file system, pre-execution blocking)\n"
                "- Deep Scanning Engine (signature-based, heuristic, YARA rules, process memory)\n"
                "- Firewall Manager (custom rules, inbound/outbound, per-app, protocol filtering)\n"
                "- Secure VPN (WireGuard, multi-region, kill switch, split tunneling)\n"
                "- Secure Vault (AES-256 encrypted quarantine, threat isolation)\n"
                "- Device & License Management (NXG-XXXX key format, device tracking)\n"
                "- Threat Intelligence (real-time alerts, IOC tracking, scan reports)\n"
                "- System Monitoring (storage analysis, startup audit, process monitoring)\n\n"
                "PLATFORMS: Windows (.msi), macOS (.dmg), Linux (AppImage), Web Dashboard\n\n"
                "PLANS:\n"
                "- Free Trial: 30 days, 1 device, limited scans, no VPN\n"
                "- Pro: Full protection, VPN, multiple devices, priority support\n"
                "- Enterprise: Maximum protection, all features, dedicated support, API access\n\n"
                "NEXGUARD DOES NOT DO:\n"
                "- Password management\n"
                "- Breach monitoring\n"
                "- Email security scanning\n"
                "- Web browsing protection\n"
                "- Identity theft protection\n\n"
                "NexGuard focuses exclusively on endpoint protection: file scanning, "
                "firewall, VPN, and device security.\n\n"
            )
            if data:
                base += "--- NEXGUARD CUSTOM INFORMATION (use this exact data) ---\n"
                if data.get("features"):
                    if isinstance(data["features"], list):
                        base += "\nFEATURES:\n" + "\n".join([f"  • {f}" for f in data["features"]])
                    else:
                        base += f"\nFeatures: {data['features']}\n"
                if data.get("pricing"):
                    base += f"""
⚠️ EXACT PRICING — USE THESE NUMBERS ONLY:
{data['pricing']}

Repeat the exact numbers above when asked about pricing.
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