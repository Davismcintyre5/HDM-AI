# ====================================================================================================
# server/services/erp/file_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from models.erp.file_extraction import FileExtraction
from loguru import logger

class ERPFileService:
    async def extract_text(self, tenant_id: str, filename: str, file_type: str, content: str = "") -> Dict[str, Any]:
        prompt = f"Extract and summarize the key information from this {file_type} file named '{filename}':\n{content[:3000]}"
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], max_tokens=1000)

        extracted = result.get("reply", "")
        await FileExtraction(tenant_id=tenant_id, filename=filename, file_type=file_type, extracted_text=extracted).insert()

        return {"filename": filename, "extracted_text": extracted, "pages": 1}

erp_file_service = ERPFileService()