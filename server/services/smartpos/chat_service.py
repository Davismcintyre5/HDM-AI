# ====================================================================================================
# 1. server/services/smartpos/chat_service.py — COMPLETE
# ====================================================================================================
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
import json
from models.smartpos.conversation import Conversation, Message, MessageRole
from services.ai_service import ai_service


class SmartPOSChatService:
    MAX_HISTORY = 15

    async def chat(
        self,
        client_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        business_id: Optional[str] = None,
        feature: str = "chat",
        data: Optional[dict] = None,
    ) -> Dict[str, Any]:
        conversation = None
        if conversation_id:
            conversation = await Conversation.get(conversation_id)
        if not conversation:
            conversation = Conversation(
                client_id=client_id,
                business_id=business_id,
                title=message[:50] + ("..." if len(message) > 50 else ""),
            )
            await conversation.insert()
            conversation_id = str(conversation.id)

        await Message(conversation_id=conversation_id, role=MessageRole.USER, content=message).insert()

        history = await Message.find(
            Message.conversation_id == conversation_id
        ).sort(-Message.timestamp).limit(self.MAX_HISTORY).to_list()
        history.reverse()
        messages = [{"role": m.role.value, "content": m.content} for m in history]

        system_prompt = self._build_system_prompt(feature, data)
        if data and feature != "public":
            data_context = self._format_data_for_ai(data, message)
            system_prompt += f"\n\n{data_context}"
        messages.insert(0, {"role": "system", "content": system_prompt})

        result = await ai_service.groq_chat(messages, max_tokens=800, service="smartpos")
        reply = result.get("reply", "Sorry, I couldn't process that.")

        await Message(conversation_id=conversation_id, role=MessageRole.ASSISTANT, content=reply, tokens_used=result.get("tokens_used", 0)).insert()

        conversation.message_count += 2
        conversation.updated_at = datetime.utcnow()
        await conversation.save()

        return {"reply": reply, "conversation_id": conversation_id, "tokens_used": result.get("tokens_used", 0)}

    def _build_system_prompt(self, feature: str, data: Optional[dict] = None) -> str:
        if feature == "public":
            base = "You are SmartPOS AI assistant. Answer questions about POS systems, features, and pricing. Be helpful and professional."
            if data:
                base += "\n\n--- SMARTPOS INFORMATION (use this exact data) ---"
                if data.get("features"):
                    base += f"\n\nFEATURES:\n" + "\n".join([f"  • {f}" for f in data["features"]])
                if data.get("pricing"):
                    p = data["pricing"]
                    base += f"\n\nPRICING (use these exact numbers):"
                    base += f"\n  • Free Trial: {p.get('trial', 'N/A')}"
                    base += f"\n  • Monthly: {p.get('monthly', 'N/A')}"
                    base += f"\n  • Yearly: {p.get('yearly', 'N/A')}"
                    base += f"\n  • One-time: {p.get('permanent', 'N/A')}"
                if data.get("support"):
                    s = data["support"]
                    base += f"\n\nSUPPORT:"
                    base += f"\n  • Email: {s.get('email', 'N/A')}"
                    base += f"\n  • Phone: {s.get('phone', 'N/A')}"
                    base += f"\n  • Hours: {s.get('hours', 'N/A')}"
                base += "\n\n⚠️ Use ONLY the exact pricing and features above. Do not invent or modify any information."
            return base
        else:
            base = "You are SmartPOS AI, a point-of-sale business assistant. Help with inventory, sales, products, customers, employees, and operations."
            if data:
                base += "\n\nREAL BUSINESS DATA has been provided below. Analyze ONLY this real data. Do NOT make up product names or numbers."
            else:
                base += "\n\nNo business data provided. If asked about inventory/sales, tell user to connect their SmartPOS system."
            return base

    def _format_data_for_ai(self, data: dict, message: str) -> str:
        parts = ["REAL BUSINESS DATA:"]
        
        # Inventory
        if "inventory" in data:
            parts.append("\n📦 INVENTORY:")
            for item in data["inventory"]:
                name = item.get("name", "Unknown")
                stock = item.get("stock", 0)
                reorder = item.get("reorder_level", 10)
                status = "⚠️ LOW" if stock <= reorder else "✅ OK"
                parts.append(f"  • {name}: {stock} units (reorder at {reorder}) — {status}")

        # Products
        if "products" in data:
            parts.append("\n🏷️ PRODUCTS:")
            for p in data["products"]:
                parts.append(f"  • {p.get('name','?')}: ${p.get('price',0)} — {p.get('stock',0)} in stock")

        # Sales data — detailed
        if "sales" in data:
            parts.append("\n💰 SALES DATA:")
            s = data["sales"]
            if "today_revenue" in s:
                parts.append(f"  Today's Revenue: KSh {s['today_revenue']}")
            if "today_transactions" in s:
                parts.append(f"  Today's Transactions: {s['today_transactions']}")
            if "total_sales" in s:
                parts.append(f"  Total Sales (30d): KSh {s['total_sales']}")
            if "transactions" in s:
                parts.append(f"  Total Transactions (30d): {s['transactions']}")
            if "top_products" in s:
                parts.append(f"  Top Products:")
                for p in s["top_products"][:5]:
                    parts.append(f"    • {p.get('name','?')}: KSh {p.get('sales',0)}")
            if "payment_methods" in s:
                parts.append(f"  Payment Methods:")
                for method, amount in s["payment_methods"].items():
                    parts.append(f"    • {method}: KSh {amount}")

        # Monthly data
        if "monthly" in data:
            parts.append("\n📊 MONTHLY OVERVIEW:")
            m = data["monthly"]
            if "total_sales" in m:
                parts.append(f"  Monthly Sales: KSh {m['total_sales']}")
            if "transactions" in m:
                parts.append(f"  Monthly Transactions: {m['transactions']}")
            if "avg_transaction" in m:
                parts.append(f"  Avg Transaction: KSh {m['avg_transaction']}")

        # Customers
        if "customers" in data:
            parts.append(f"\n👥 CUSTOMERS ({len(data['customers'])} records):")
            for c in data["customers"][:5]:
                parts.append(f"  • {c.get('name','?')}: {c.get('visitCount',0)} visits, KSh {c.get('totalSpent',0)} spent")

        parts.append(f"\n\nUser question: {message}")
        parts.append("\nAnalyze this real data and answer using specific names and numbers from the data above. Do NOT make up data.")
        return "\n".join(parts)


smartpos_chat_service = SmartPOSChatService()