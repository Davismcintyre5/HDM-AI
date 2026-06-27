# ====================================================================================================
# HDM AI Engine - services/erp/file_service.py
# Stateless — MERN logs usage, Python does AI only
# ====================================================================================================

from typing import Dict, Any
from services.ai_service import ai_service
from loguru import logger


class ERPFileService:
    async def extract_text(
        self, tenant_id: str, filename: str, file_type: str,
        content: str = "", data: dict = None,
    ) -> Dict[str, Any]:
        context_parts = [f"File: {filename} (Type: {file_type})"]
        if data:
            context_parts.append("\n--- RELATED BUSINESS DATA ---")
            if "invoices" in data:
                for inv in data["invoices"][:5]:
                    context_parts.append(f"  • {inv.get('number','?')}: {inv.get('customer','?')} — {inv.get('amount',0)}")
            if "products" in data:
                for prod in data["products"][:5]:
                    context_parts.append(f"  • {prod.get('name','?')}: Stock {prod.get('stock',0)}")
        context_parts.append(f"\n--- FILE CONTENT ---\n{content[:5000] if content else '[No content]'}")
        context_parts.append("\n\nExtract key information from this file. Be specific with numbers and names.")

        prompt = "\n".join(context_parts)
        result = await ai_service.groq_chat(
            [{"role": "user", "content": prompt}],
            max_tokens=1000,
            module="erp",
        )
        extracted = result.get("reply", "Could not extract text.")

        logger.info(f"File extracted: {filename} ({len(extracted)} chars)")
        return {
            "filename": filename,
            "extracted_text": extracted,
            "pages": 1,
            "data_analyzed": data is not None,
        }


erp_file_service = ERPFileService()