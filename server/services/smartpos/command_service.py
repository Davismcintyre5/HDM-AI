# ====================================================================================================
# server/services/smartpos/command_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from loguru import logger

class CommandService:
    INTENTS = ["add_product", "check_stock", "generate_report", "apply_discount", "process_return", "view_sales", "manage_employee", "update_price"]

    async def execute(self, business_id: str, command: str, parameters: dict = None) -> Dict[str, Any]:
        prompt = f"""Analyze this POS command: "{command}"
Available intents: {', '.join(self.INTENTS)}
Return JSON: {{"intent": "one of the above", "confidence": 0.0-1.0, "parameters": {{}}, "response": "what to tell the user"}}"""

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=300)
        try:
            import json
            data = json.loads(result.get("reply", "{}"))
            return {"success": True, "intent": data.get("intent", ""), "result": data.get("response", ""), "parameters": data.get("parameters", {})}
        except:
            return {"success": False, "intent": "", "result": "Could not understand command. Try: add product, check stock, generate report."}

command_service = CommandService()