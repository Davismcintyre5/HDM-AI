# ====================================================================================================
# server/services/smartpos/chat_service.py
# ====================================================================================================
"""
HDM AI - SmartPOS Chat Service
Real data analysis for landing page and client dashboard
"""

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
        """Process chat with optional real business data."""

        # Get or create conversation
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

        # Save user message
        await Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message,
        ).insert()

        # Build message history
        history = await Message.find(
            Message.conversation_id == conversation_id
        ).sort(-Message.timestamp).limit(self.MAX_HISTORY).to_list()
        history.reverse()
        messages = [{"role": m.role.value, "content": m.content} for m in history]

        # Build system prompt based on feature and data
        system_prompt = self._build_system_prompt(feature, data)

        # Add real data context if provided
        if data:
            data_context = self._format_data_for_ai(data, message)
            system_prompt += f"\n\n{data_context}"

        messages.insert(0, {"role": "system", "content": system_prompt})

        # Call AI
        result = await ai_service.groq_chat(messages, max_tokens=800)
        reply = result.get("reply", "Sorry, I couldn't process that.")

        # Save assistant message
        await Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=reply,
            tokens_used=result.get("tokens_used", 0),
        ).insert()

        # Update conversation
        conversation.message_count += 2
        conversation.updated_at = datetime.utcnow()
        await conversation.save()

        return {
            "reply": reply,
            "conversation_id": conversation_id,
            "tokens_used": result.get("tokens_used", 0),
        }

    def _build_system_prompt(self, feature: str, data: Optional[dict] = None) -> str:
        """Build system prompt based on feature type."""

        if feature == "public":
            base = (
                "You are SmartPOS AI assistant. Answer questions about the SmartPOS system, "
                "its features, pricing, and capabilities. Be helpful and professional. "
                "Encourage visitors to sign up for a free trial."
            )
        else:
            base = (
                "You are SmartPOS AI, a point-of-sale business assistant. "
                "Help with inventory, sales, products, customers, employees, and business operations. "
                "Be concise, accurate, and professional."
            )

        # If data is provided, instruct AI to use it
        if data:
            base += (
                "\n\nREAL BUSINESS DATA has been provided below. "
                "Analyze ONLY this real data — do NOT make up or guess any product names, numbers, or details. "
                "If the data doesn't contain what the user is asking for, say so. "
                "Use specific names, quantities, and values from the actual data."
            )
        else:
            base += (
                "\n\nNo business data has been provided. "
                "If the user asks about their inventory, sales, products, or business metrics, "
                "tell them: 'I need access to your real data to answer that. Please connect your SmartPOS system.' "
                "Do NOT make up fake product names or numbers."
            )

        return base

    def _format_data_for_ai(self, data: dict, message: str) -> str:
        """Format real business data for AI analysis."""

        parts = ["REAL BUSINESS DATA:"]

        # Inventory data
        if "inventory" in data:
            parts.append("\n📦 INVENTORY:")
            for item in data["inventory"]:
                name = item.get("name", "Unknown")
                stock = item.get("stock", 0)
                reorder = item.get("reorder_level", 0)
                status = "⚠️ LOW" if stock <= reorder else "✅ OK"
                parts.append(f"  • {name}: {stock} units (reorder at {reorder}) — {status}")

        # Products data
        if "products" in data:
            parts.append("\n🏷️ PRODUCTS:")
            for p in data["products"]:
                parts.append(f"  • {p.get('name', 'Unknown')}: ${p.get('price', 0)} — {p.get('stock', 0)} in stock")

        # Sales data
        if "sales" in data:
            parts.append(f"\n💰 SALES: Total: ${data['sales'].get('total', 0)} | Transactions: {data['sales'].get('transactions', 0)}")

        # Customers data
        if "customers" in data:
            parts.append(f"\n👥 CUSTOMERS: {len(data['customers'])} records")
            for c in data["customers"][:5]:
                parts.append(f"  • {c.get('name', 'Unknown')}: {c.get('total_purchases', 0)} purchases")

        # Employees data
        if "employees" in data:
            parts.append(f"\n👤 EMPLOYEES: {len(data['employees'])} records")
            for e in data["employees"][:5]:
                parts.append(f"  • {e.get('name', 'Unknown')}: {e.get('role', 'Staff')}")

        # Raw data dump for any other data types
        other_data = {k: v for k, v in data.items() if k not in ["inventory", "products", "sales", "customers", "employees"]}
        if other_data:
            parts.append(f"\n📊 OTHER DATA:\n{json.dumps(other_data, indent=2)[:2000]}")

        parts.append(f"\n\nUser question: {message}")
        parts.append("\nAnalyze this real data and answer the question using specific names and numbers from the data above.")

        return "\n".join(parts)


smartpos_chat_service = SmartPOSChatService()