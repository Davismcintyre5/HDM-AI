# ====================================================================================================
# HDM AI Engine - services/erp/query_service.py
# Stateless — MERN logs usage, Python does AI only
# ====================================================================================================

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from services.ai_service import ai_service
from loguru import logger
import json
import hashlib
import asyncio

_cache: Dict[str, tuple] = {}
CACHE_DURATION = timedelta(minutes=15)
MIN_REQUEST_INTERVAL = 0.3
_last_request_time = 0.0


class ERPQueryService:

    async def process_query(
        self, tenant_id: str, query: str, provider: str = "groq",
        context: Optional[Dict] = None, data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        global _last_request_time

        cache_key = hashlib.md5(
            f"{tenant_id}:{query}:{json.dumps(context or {}, sort_keys=True)}:{json.dumps(data or {}, sort_keys=True)}".encode()
        ).hexdigest()

        if cache_key in _cache:
            cached_response, expiry = _cache[cache_key]
            if datetime.utcnow() < expiry:
                logger.info(f"ERP cache hit for tenant={tenant_id}")
                return cached_response

        now = datetime.utcnow().timestamp()
        time_since_last = now - _last_request_time
        if time_since_last < MIN_REQUEST_INTERVAL and time_since_last > 0:
            wait_time = MIN_REQUEST_INTERVAL - time_since_last
            if wait_time < 5:
                await asyncio.sleep(wait_time)
        _last_request_time = datetime.utcnow().timestamp()

        messages = []
        system_parts = [
            "You are HDM ERP AI, the intelligent assistant for HDM's Enterprise Resource Planning platform.",
            "Analyze REAL business data and answer accurately. NEVER say 'no data provided' if data exists.",
            "Use specific numbers, names, and amounts. Be professional and helpful.",
        ]

        # Landing page context
        if context:
            if context.get("source") == "landing":
                system_parts.append("""
You are speaking to a POTENTIAL CUSTOMER visiting the HDM ERP landing page.
They are NOT an existing user and do NOT have an ERP system connected.
Do NOT ask them to "connect your ERP system" or "provide business data".
Do NOT tell them to "connect their system" — they don't have one yet.

Instead:
- Answer their questions about features, pricing, plans, payment methods, and support
- Use ONLY the information provided below
- Be friendly and helpful
- Encourage them to sign up for a free trial or contact support
- Mention the free trial when relevant
""")

                if context.get("payment_methods"):
                    system_parts.append(f"Payment methods: {context['payment_methods']}")
                if context.get("locations"):
                    system_parts.append(f"Locations: {context['locations']}")
                if context.get("contacts"):
                    system_parts.append(f"Contacts: {json.dumps(context['contacts'])}")
                if context.get("features"):
                    system_parts.append(f"Features: {context['features']}")
                if context.get("pricingSummary"):
                    system_parts.append(f"""
⚠️ EXACT PRICING — USE THESE NUMBERS ONLY. DO NOT MODIFY, ROUND, OR GUESS:
{context['pricingSummary']}

Repeat the exact numbers above when asked about pricing. Do not invent smaller numbers.
""")
                system_parts.append("Answer the visitor's question using ONLY the information above. Do not make up details.")

            # Tenant context
            if context.get("source") == "tenant" and context.get("tenant_info"):
                system_parts.append(f"\n--- TENANT CONTEXT ---")
                system_parts.append(f"Tenant: {json.dumps(context['tenant_info'])}")

        # Real ERP data
        if data:
            system_parts.append("\n--- REAL ERP DATA ---")
            if "summary" in data:
                system_parts.append("\nQUICK SUMMARY:")
                for key, value in data["summary"].items():
                    system_parts.append(f"  {key}: {value}")
            if "invoices" in data:
                system_parts.append(f"\nINVOICES ({len(data['invoices'])}):")
                for inv in data["invoices"][:10]:
                    system_parts.append(f"  • {inv.get('number','?')}: {inv.get('customer','?')} — {inv.get('amount',0)} ({inv.get('status','?')})")
            if "products" in data:
                system_parts.append(f"\nPRODUCTS ({len(data['products'])}):")
                for p in data["products"][:10]:
                    w = " ⚠️ LOW" if p.get('stock', 0) <= p.get('reorderLevel', 10) else ""
                    system_parts.append(f"  • {p.get('name','?')}: Stock {p.get('stock',0)}, Price {p.get('sellingPrice',0)}{w}")
            if "employees" in data:
                system_parts.append(f"\nEMPLOYEES ({len(data['employees'])}):")
                for e in data["employees"][:5]:
                    system_parts.append(f"  • {e.get('name','?')}: {e.get('position','?')} — {e.get('department','?')}")
            system_parts.append("\n⚠️ Use ONLY the real data above. Reference specific numbers, names, and amounts.")
        else:
            system_parts.append("\n⚠️ No business data provided. Tell user to connect their ERP system to unlock insights.")

        messages.append({"role": "system", "content": "\n".join(system_parts)})
        messages.append({"role": "user", "content": query})

        result = await ai_service.groq_chat(messages, max_tokens=1500, module="erp")
        reply = result.get("reply", "") or "Could not process query."

        response_data = {
            "reply": reply, "provider": provider,
            "tokens_used": result.get("tokens_used", 0),
            "data_analyzed": data is not None,
        }
        if result.get("success"):
            _cache[cache_key] = (response_data, datetime.utcnow() + CACHE_DURATION)

        return response_data


erp_query_service = ERPQueryService()