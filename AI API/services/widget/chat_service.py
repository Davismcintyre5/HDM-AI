from typing import Dict, Any, Optional
from services.ai_service import ai_service

class WidgetChatService:
    MAX_HISTORY = 15

    async def chat(self, source: str, message: str, messages: Optional[list] = None, user_id: Optional[str] = None, context: Optional[dict] = None, data: Optional[dict] = None) -> Dict[str, Any]:
        history = messages or []
        history.append({"role": "user", "content": message})

        system = self._build_system_prompt(source, context, data)
        history.insert(0, {"role": "system", "content": system})

        result = await ai_service.groq_chat(history, max_tokens=800, module="widget")
        reply = result.get("reply", "Sorry, I couldn't process that.")

        return {"reply": reply, "source": source, "tokens_used": result.get("tokens_used", 0)}

    def _build_system_prompt(self, source: str, context: Optional[dict] = None, data: Optional[dict] = None) -> str:
        system_prompts = {
            "docusoft": "You are DocuSoft AI. Help with documents, pricing, and purchases.",
            "hdm_portfolio": "You are HDM Portfolio AI. Answer questions about our company, services, apps, and projects."
        }
        system = system_prompts.get(source, system_prompts["hdm_portfolio"])

        d = data or {}
        c = context or {}

        services = d.get("services") or c.get("services")
        apps = d.get("apps") or c.get("apps")
        projects = d.get("projects") or c.get("projects")
        company = d.get("company") or c.get("company")
        social = d.get("socialLinks") or c.get("socialLinks")
        documents = d.get("documents") or c.get("documents")
        software = d.get("software") or c.get("software")
        paymentMethods = d.get("paymentMethods") or c.get("paymentMethods")
        pricing = d.get("pricing") or c.get("pricing")
        categories = d.get("categories") or c.get("categories")

        parts = ["\n\nAnswer questions using ONLY the information provided below. Do NOT invent anything."]

        if company:
            parts.append(f"\nCOMPANY: {company.get('name','')} | {company.get('email','')} | {company.get('phone','')}")

        if services:
            parts.append("\nOUR SERVICES:")
            for s in services:
                name = s.get("title") or s.get("name", "")
                desc = s.get("description", "")
                parts.append(f"  • {name}: {desc}" if desc else f"  • {name}")

        if apps:
            parts.append("\nOUR APPS:")
            for a in apps:
                name = a.get("title") or a.get("name", "")
                desc = a.get("description", "")
                parts.append(f"  • {name}: {desc}" if desc else f"  • {name}")
            parts.append("When asked about apps, list all apps above.")

        if projects:
            parts.append("\nOUR PROJECTS:")
            for p in projects:
                name = p.get("title") or p.get("name", "")
                desc = p.get("description", "")
                parts.append(f"  • {name}: {desc}" if desc else f"  • {name}")

        if documents:
            parts.append("\nDOCUMENTS FOR SALE:")
            for doc in documents:
                name = doc.get("title") or doc.get("name", "")
                desc = doc.get("description", "")
                price = doc.get("price", 0)
                line = f"  • {name}: KSh {price}"
                if desc:
                    line += f" — {desc}"
                parts.append(line)
            parts.append("When asked what's for sale, list all documents above with prices.")

        if software:
            parts.append("\nSOFTWARE FOR SALE:")
            for sw in software:
                name = sw.get("title") or sw.get("name", "")
                desc = sw.get("description", "")
                price = sw.get("price", 0)
                line = f"  • {name}: KSh {price}"
                if desc:
                    line += f" — {desc}"
                parts.append(line)

        if categories:
            if isinstance(categories, list):
                cat_names = []
                for cat in categories:
                    if isinstance(cat, dict):
                        cat_names.append(cat.get("title") or cat.get("name", ""))
                    else:
                        cat_names.append(str(cat))
                parts.append(f"\nCATEGORIES: {', '.join(cat_names)}")
            else:
                parts.append(f"\nCATEGORIES: {categories}")

        if pricing:
            parts.append(f"\nPRICING INFO: {pricing}")

        if paymentMethods:
            parts.append("\nPAYMENT METHODS:")
            for pm in paymentMethods:
                name = pm.get("title") or pm.get("name", "")
                desc = pm.get("description", "")
                parts.append(f"  • {name}: {desc}" if desc else f"  • {name}")

        if social:
            parts.append(f"\nLINKS: {', '.join(social.keys())}")

        system += "\n".join(parts)

        return system

widget_chat_service = WidgetChatService()