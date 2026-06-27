# ====================================================================================================
# HDM AI Engine - schemas/erp/file.py
# ====================================================================================================

from pydantic import BaseModel, Field
from typing import Optional


class FileExtractRequest(BaseModel):
    tenant_id: str
    filename: str
    file_type: str
    content: Optional[str] = ""
    data: Optional[dict] = None


class FileExtractResponse(BaseModel):
    filename: str
    extracted_text: str = ""
    pages: int = 0